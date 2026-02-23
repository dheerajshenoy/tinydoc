import os
import sys

class Parser:
    def __init__(self):
        self.HOME: str | None = os.getenv("HOME")
        self.file = None
        self.lines = None
        # Standard keywords to look for in comments
        self.keywords = ["desc", "choice", "type", "default", "note"]

    def __open(self, file: str):
        if file.startswith("~"):
            file = file.replace("~", self.HOME)
        self.file = file

        if not os.path.isfile(file):
            raise FileNotFoundError(f"Could not find file: {file}")

        try:
            with open(self.file, "r") as f:
                self.lines = [line.strip() for line in f.readlines()]
        except OSError:
            print(f"Could not open file: {self.file}")
            sys.exit(-1)

    def parse(self, path: str):
        self.__open(path)

        sections = []
        current_section = None
        current_tags = {}
        active_block_key = None

        for line in self.lines:
            line = line.strip()
            if not line:
                continue

            # 1. HANDLE TAG LINES (// @key ...)
            if line.startswith("// @"):
                content = line[4:].strip()
                key, _, value = content.partition(" ")
                key, value = key.strip(), value.strip()

                # Section Start
                if key == "section":
                    current_section = {
                        "name": value,
                        "fields": [],
                        "section_desc": None,
                        "section_type": None
                    }
                    current_tags = {}

                # Section End
                elif key == "endsection":
                    if current_section:
                        sections.append(current_section)
                    current_section = None

                # Global Section Metadata (e.g., @section_desc)
                elif current_section and key.startswith("section_"):
                    current_section[key] = value

                # Field Metadata (e.g., @desc, @default)
                elif key in self.keywords:
                    if value.startswith("{"):
                        if value.endswith("}"):
                            current_tags[key] = value[1:-1].strip()
                        else:
                            active_block_key = key
                            current_tags[key] = value[1:].strip()
                    else:
                        current_tags[key] = value

            # 2. HANDLE MULTI-LINE BLOCK CONTINUATION (inside { ... })
            elif line.startswith("//") and active_block_key:
                content = line[2:].strip()
                if content.endswith("}"):
                    current_tags[active_block_key] += " " + content[:-1].strip()
                    active_block_key = None
                else:
                    current_tags[active_block_key] += " " + content

            # 3. HANDLE ACTUAL CODE LINES (C++ Field Declarations)
            elif current_section and current_tags and not line.startswith("//"):
                # Ignore lines that define the struct itself to prevent "ghost" fields
                if line.startswith("struct") or line.startswith("static struct"):
                    # If we had tags sitting above 'struct window',
                    # they likely belong to the section description.
                    if "desc" in current_tags:
                        current_section["section_desc"] = current_tags.pop("desc")
                    continue

                # Extract variable name: "bool fullscreen{false};" -> "bool fullscreen"
                code_part = line.split("{")[0].strip()
                if code_part:
                    parts = code_part.split()
                    if parts:
                        # The last word is the variable name
                        current_tags["name"] = parts[-1]

                        # Infer type if @type tag was missing
                        if "type" not in current_tags:
                            current_tags["type"] = " ".join(parts[:-1])

                        current_section["fields"].append(current_tags)
                        current_tags = {}

        return sections

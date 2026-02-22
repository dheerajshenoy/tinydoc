import os
import sys

class Parser:

    def __init__(self):
        self.HOME : str | None = os.getenv("HOME")
        self.file = None
        self.lines = None
        self.keywords = [ "@desc", "@choice", "@type", "@default" ]
        self.docobjs = []

    def __open(self, file: str):
        """
        Helper function to open file
        """
        if file.startswith("~"):
            file = file.replace("~", self.HOME)
        self.file = file

        if not os.path.isfile(file):
            raise FileNotFoundError("Could not find file ", file)

        try:
            with open(self.file, "r") as f:
                self.lines = [line.strip() for line in f.readlines()]
        except OSError:
            print("Could not open file", self.file)
            sys.exit(-1)

    def parse(self, path: str):
        self.__open(path)

        sections = []
        current_section = None
        current_tags = {}
        section_prop_check = False

        for line in self.lines:
            line = line.strip()
            if line.startswith("// @"):
                key, _, value = line[4:].partition(" ")

                if key == "section":
                    current_section = {"name": value.strip(), "fields": [], "section_desc": None, "section_type": None }

                elif key.startswith("section_"):
                    current_section[key] = value.strip()


                elif key == "endsection":
                    sections.append(current_section)
                    current_section = None
                else:
                    current_tags[key] = value.strip()


            elif current_section and current_tags:
                current_tags["name"] = line.split("{")[0].split()[-1]
                current_section["fields"].append(current_tags)
                current_tags = {}


        return sections

from tinydoc.parser import Parser
import json

def main():
    parser = Parser()
    docobjs = parser.parse("~/Gits/lektra/src/Config.hpp")

    with open("/home/dheeraj/Gits/dheerajshenoy.github.io/lektra-files/config.json", 'w') as f:
        json.dump(docobjs, f, indent=4)


if __name__ == "__main__":
    main()

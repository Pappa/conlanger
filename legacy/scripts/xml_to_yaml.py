import yaml
from lxml import html, etree
import argparse
import re

default = etree.Element('default')
default.text = ""

def xml_to_yaml(input_path, output_path):

    results = []
    tree = etree.parse(input_path)
    sections = tree.getroot().findall('section')
    for section in sections:
        idx = section.attrib['index']
        name = section.attrib['name']

        cite = section.find('cite')
        cite_text = cite.text if cite is not None else ""
        cite_text = ' '.join(cite_text.splitlines())
        cite_text = re.sub(r"\s+", " ", cite_text, flags=re.UNICODE).strip()

        result = {
            "section": name,
            "index": idx,
        }

        if cite_text:
            result["citation"] = cite_text

        rules = section.findall('rule')

        if len(rules) > 0:
            result["rules"] = []
        for rule in rules:
            sporadic = rule.attrib.get('sporadic', 'false') == 'true'

            input = rule.find('input')
            input_text = input.text if input is not None else ""

            output = rule.find('output')
            output_text = output.text if output is not None else ""

            env = rule.find('env')
            env_text = env.text if env is not None else ""

            exception = rule.find('exception')
            exception_text = exception.text if exception is not None else ""

            rule_result = {
                "input": input_text,
                "output": output_text,
            }

            if env_text:
                rule_result["env"] = env_text

            if exception_text:
                rule_result["exception"] = exception_text

            if sporadic:
                rule_result["sporadic"] = True

            result["rules"].append(rule_result)

        results.append(result)

    final_yaml = yaml.dump({"sections": results}, allow_unicode=True, sort_keys=False, default_flow_style=False, width=1024, default_style=None)
    with open(output_path, 'w') as f:
        f.write(final_yaml)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    xml_to_yaml(args.input, args.output)
    print("Done")
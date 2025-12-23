"""
Quick script to convert YAML files to TOML format
Usage: python convert_yaml_to_toml.py <input.yaml> <output.toml>
"""

import sys
import yaml
import tomli_w

if len(sys.argv) != 3:
    print("Usage: python convert_yaml_to_toml.py <input.yaml> <output.toml>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Load YAML
with open(input_file, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Write TOML
with open(output_file, 'wb') as f:
    tomli_w.dump(data, f)

print(f"Converted {input_file} -> {output_file}")

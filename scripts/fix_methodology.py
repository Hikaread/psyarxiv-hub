import re, sys

files = [
    "625-4yhev_v1.md",
    "626-f2cjw_v2.md",
    "627-e9rz8_v1.md",
    "628-5p28m_v2.md",
    "629-5bzjp_v2.md",
    "630-9u8kw_v1.md",
    "631-b6n52_v1.md",
]

base = "/home/z/my-project/psyarxiv-hub/curation/inbox"

for fname in files:
    path = f"{base}/{fname}"
    with open(path, "r") as f:
        content = f.read()
    
    # Find the Methodology Note section
    # We need to handle the regex carefully - find between ## Methodology Note and next ## 
    idx_start = content.find("## Methodology Note\n")
    if idx_start == -1:
        print(f"SKIP {fname}: no Methodology Note found")
        continue
    
    # Find the next ## after the methodology note header
    after_header = content[idx_start + len("## Methodology Note\n"):]
    # Find next ## heading
    next_heading = re.search(r'\n## ', after_header)
    if next_heading:
        meth_body = after_header[:next_heading.start()]
        rest_of_file = after_header[next_heading.start():]
    else:
        meth_body = after_header
        rest_of_file = ""
    
    # Count dimensions
    dims = re.findall(r'(__[A-Za-z\s]+__\s*:)', meth_body)
    if len(dims) <= 1:
        print(f"SKIP {fname}: only {len(dims)} dimension(s), nothing to split")
        continue
    
    # Check if already formatted (has blank lines between dimensions)
    # Split the body into lines and check
    lines = meth_body.strip().split('\n')
    if len(lines) > 3:  # already multi-line
        print(f"SKIP {fname}: already {len(lines)} lines, seems formatted")
        continue
    
    # It's a single paragraph - split at each __Dimension__:
    # First, separate intro text from dimension blocks
    first_dim_match = re.search(r'(__[A-Za-z\s]+__\s*:)', meth_body)
    if not first_dim_match:
        print(f"SKIP {fname}: no dimensions found")
        continue
    
    intro = meth_body[:first_dim_match.start()].strip()
    dim_text = meth_body[first_dim_match.start():]
    
    # Split dim_text at each __Dimension__: boundary
    # Each dimension starts with __Name__:
    parts = re.split(r'(?=__\w)', dim_text)
    parts = [p.strip() for p in parts if p.strip()]
    
    if intro:
        new_body = intro + "\n\n" + "\n\n".join(parts)
    else:
        new_body = "\n\n".join(parts)
    
    new_section = "## Methodology Note\n" + new_body.strip() + "\n"
    
    # Reconstruct file
    new_content = content[:idx_start] + new_section + rest_of_file
    
    with open(path, "w") as f:
        f.write(new_content)
    
    print(f"FIXED {fname}: {len(dims)} dimensions split into paragraphs")
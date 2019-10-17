import re

# clip coordinates in a geoJSON to six decimal digits.
def clip(infile, outfile=None):

    if outfile is None:
        outfile = infile
    with open (infile, 'r' ) as f:
        content = f.read()

    content_new = re.sub('([0-9]+\.[0-9]{6})([0-9]+)', r'\1', content,
        flags = re.M)

    with open(outfile, 'w') as f:
        f.write(content_new)

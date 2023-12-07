import codecs
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import this

import_this_output = codecs.decode(this.s, 'rot13')
for i, line in enumerate(import_this_output.splitlines()[2:], start=1):
    print(i, line)

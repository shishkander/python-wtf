# Python WTF: When you only trust the kernel.

This is a toolkit for debugging multiprocessing python app that hijacks normal
logging and stdout. Basic usage is like this:

```python
import wtf
wtf.log('something')
```


### Realistic example

See `example_before.py` and `example_after.py` in this repository.

```bash
# Run the debug version:
python example_after.py 32
# And now can you see your logs:
cat /tmp/wtf/example_after.py_16* | sort | vi -
# Don't forgot to move/delete them before next run.
mv /tmp/wtf /tmp/first_run   # OR $ rm -rf /tmp/wtf
```

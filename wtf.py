import datetime
import errno
import inspect
import os
import sys
import threading
import traceback


_lock = threading.RLock()  # THE lock to mutate module structures.
_locks_and_files = {}
_conf = {
    'path': '/tmp/wtf',
    'file_per_thread': False,
}
_first_time = True


def reconfigure(**kwargs):
  global _conf
  global _first_time
  with _lock:
    _conf = _new_conf(**kwargs)
    _first_time = True


def log(fmt_or_str, *fmt_args, **kwargs):
  _, filename, lineno, _, _, _ = inspect.stack()[1]
  try:
    msg = fmt_or_str % fmt_args
  except (KeyboardInterrupt, SystemError):
    raise
  except:
    msg = "failed to format line %s with format string %s" % (
        lineno, fmt_or_str)

  thread = threading.current_thread()
  prefix = '%s %+20s:%-4s %s-%s-%s%-30s' % (
      # For this kind of logging, date is not important actually.
      str(datetime.datetime.now())[len("2016-16-13 "):],
      filename, lineno,
      os.getpid(), thread.ident, 'D' if thread.daemon else 'N',
      '(%s)' % thread.name)
  return _write('%+50s: %s\n' % (prefix, msg), _new_conf(**kwargs))


def _new_conf(**kwargs):
  unknown = set(kwargs).difference(_conf)
  if unknown:
    fmt = 'unknown config parameters: [%s] (valid params: %s)'
    # Sorted to make strings deterministic.
    params_to_str = lambda x: ''.join(sorted(str(s) for s in x))
    assert not unknown, fmt % (params_to_str(unknown), params_to_str(_conf))
    raise SystemError("test with assertions enabled first!")
  with _lock:
    copy = _conf.copy()
  copy.update(**kwargs)
  return copy


def _maybe_init():
  global _first_time
  if not _first_time:
    return
  with _lock:
    if not _first_time:
      return
    try:
      os.makedirs(_conf['path'])
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise
    if not os.path.exists(_conf['path']):
      raise Exception("failed to create directory: %s", _conf['path'])
    _first_time = False


def _get_lock_and_file(conf):
  tid = threading.current_thread().ident
  key = tid if conf['file_per_thread'] else 'process'
  try:
    return _locks_and_files[key]
  except KeyError:
    path_prefix = os.path.join(conf['path'],
                               '%s_%s' % (sys.argv[0] or 'python', os.getpid()))
    with _lock:
      _maybe_init()
      try:
        return _locks_and_files[key]
      except KeyError:
        ret = _locks_and_files[key] = (
            (threading.RLock(), '%s_%s.log' % (path_prefix, tid))
            if conf['file_per_thread'] else
            (_lock, path_prefix + '.log')
        )
        return ret


def _write(msg, conf):
  lock, logfile_path = _get_lock_and_file(conf)
  with lock:
    with open(logfile_path, 'a') as f:
      f.write(msg)

import multiprocessing
import sys
import time
import wtf  # Add this.

def inverse(arg):
  p, i = arg
  # Fermat's theorem
  #   i**(-1) % PRIME == (i**(p-2)) % PRIME
  # So, let's do fast exponentiation here.
  res = 1
  cur = i
  k = p - 2
  while k:
    if k % 2:
      res = (res * cur) % p
    k /= 2
    cur = (cur * cur) % p
  wtf.log('processed %s => %i', arg, res)  # Add this.
  return res

def main(args):
  num = int(args[0]) if args else 2
  prime = int(args[1]) if args[1:] else 100003

  start = time.time()
  pool = multiprocessing.Pool(num)
  res = pool.map(inverse, ((prime, i) for i in xrange(prime)))
  pool.close()
  pool.join()
  took = time.time() - start

  if set(xrange(prime)) != set(res):
    print('Are you sure %i is prime? Unique inverses: %i' % (
        prime, len(set(res))))
  else:
    print('Verified that set of integers modulo prime %i '
          'is closed under inverse operation' % prime)
  print 'took: %.3f seconds with %i worker processes' % (took, num)
  return 0


if __name__ == '__main__':
  # Choose your prime: https://primes.utm.edu/lists/small/100000.txt
  sys.exit(main(sys.argv[1:]))

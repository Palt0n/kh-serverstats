import collections

class UniqueDict(dict):
    def __init__(self, inp=None):
        if isinstance(inp,dict):
            super(UniqueDict,self).__init__(inp)
        else:
            super(UniqueDict,self).__init__()
            if isinstance(inp, (collections.Mapping, collections.Iterable)): 
                si = self.__setitem__
                for k,v in inp:
                    si(k,v)

    def __setitem__(self, k, v):
        try:
            self.__getitem__(k)
            raise ValueError("duplicate key '{0}' found".format(k))
        except KeyError:
            super(UniqueDict,self).__setitem__(k,v)

def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)
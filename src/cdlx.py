import ctypes


lib = ctypes.CDLL("lib/dlx.dll")


# ivec api
class IVec(ctypes.Structure):
  _fields_ = [("data", ctypes.POINTER(ctypes.c_uint32)),
              ("size", ctypes.c_size_t),
              ("capacity", ctypes.c_size_t)]

lib.ivec_init.argtypes = (ctypes.POINTER(IVec),)
lib.ivec_init.restype = None
lib.ivec_destroy.argtypes = (ctypes.POINTER(IVec),)
lib.ivec_destroy.restype = None


# results API
class Results(ctypes.Structure):
  _fields_ = [("data", IVec),
              ("idxs", IVec)]

lib.results_init.argtypes = (ctypes.POINTER(Results),)
lib.results_init.restype = None
lib.results_destroy.argtypes = (ctypes.POINTER(Results),)
lib.results_destroy.restype = None
lib.results_print.argtypes = (ctypes.POINTER(Results),)
lib.results_print.restype = None


# ecp api
class ECP(ctypes.Structure):
  _fields_ = [("U", ctypes.POINTER(ctypes.c_uint32)),
              ("u_size", ctypes.c_size_t),
              ("S", ctypes.POINTER(ctypes.c_uint32)),
              ("s_idxs", ctypes.POINTER(ctypes.c_uint32)),
              ("s_size", ctypes.c_size_t)]
  
lib.ecp_init.argtypes          = (ctypes.POINTER(ECP),)
lib.ecp_init.restype           = None
lib.ecp_destroy.argtypes       = (ctypes.POINTER(ECP),)
lib.ecp_destroy.restype        = None
lib.ecp_push_universe.argtypes = (ctypes.POINTER(ECP), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32)
lib.ecp_push_universe.restype  = None
lib.ecp_push_subset.argtypes   = (ctypes.POINTER(ECP), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32)
lib.ecp_push_subset.restype    = None
lib.ecp_solve.argtypes         = (ctypes.POINTER(ECP), ctypes.POINTER(Results))
lib.ecp_solve.restype          = None


def solve_cdlx(U, S):

  # Initialize ECP
  ecp = ECP()
  lib.ecp_init(ctypes.byref(ecp))
  c_U = (ctypes.c_uint32 * len(U))(*U)
  lib.ecp_push_universe(ctypes.byref(ecp), c_U, len(U))
  for i, si in enumerate(S):
    c_si    = (ctypes.c_uint32 * len(si))(*si)
    lib.ecp_push_subset(ctypes.byref(ecp), c_si, len(si))

  # Initialize results container
  results = Results()
  lib.results_init(ctypes.byref(results))

  # Solve the problem
  lib.ecp_solve(ctypes.byref(ecp), ctypes.byref(results))

  # Build solutions
  idxs = [results.idxs.data[i] for i in range(results.idxs.size)]
  solutions = []
  for (s, e) in zip([0] + idxs, idxs):
    solutions.append(results.data.data[s:e])

  # Print results
  # lib.results_print(ctypes.byref(results))

  # Free resources
  lib.results_destroy(ctypes.byref(results))
  lib.ecp_destroy(ctypes.byref(ecp))

  return solutions
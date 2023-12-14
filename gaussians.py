# -----------------------------------------------------------------------------
# This file contains a collection of functions which are linear combinations
# of some number of Gaussians. The functions are named "gn()" where n is the 
# number of gaussians in the linear combination.
# -----------------------------------------------------------------------------

import numpy as np


def g1(x, a1,c1,s1):
    """
    A single gaussian function, centered at c1 with standard deviation s1, and
    amplitude a1.
    """
    return (a1/(s1*(np.sqrt(2*np.pi)))) * np.exp((-1.0/2.0)*(((x-c1)/s1)**2))
             
def g2(x, a1,c1,s1, a2,c2,s2):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2)

def g3(x, a1,c1,s1, a2,c2,s2, a3,c3,s3):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3)

def g4(x, a1,c1,s1, a2,c2,s2, a3,c3,s3, a4,c4,s4):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3) + \
           g1(x, a4,c4,s4)

def g5(x, a1,c1,s1, a2,c2,s2, a3,c3,s3, a4,c4,s4, a5,c5,s5):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3) + \
           g1(x, a4,c4,s4) + g1(x, a5,c5,s5)

def g6(x, a1,c1,s1, a2,c2,s2, a3,c3,s3, a4,c4,s4, a5,c5,s5,
       a6,c6,s6):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3) + \
           g1(x, a4,c4,s4) + g1(x, a5,c5,s5) + g1(x, a6,c6,s6)

def g7(x, a1,c1,s1, a2,c2,s2, a3,c3,s3, a4,c4,s4, a5,c5,s5,
       a6,c6,s6, a7,c7,s7):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3) + \
           g1(x, a4,c4,s4) + g1(x, a5,c5,s5) + g1(x, a6,c6,s6) + \
           g1(x, a7,c7,s7)

def g8(x, a1,c1,s1, a2,c2,s2, a3,c3,s3, a4,c4,s4, a5,c5,s5,
       a6,c6,s6, a7,c7,s7, a8,c8,s8):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3) + \
           g1(x, a4,c4,s4) + g1(x, a5,c5,s5) + g1(x, a6,c6,s6) + \
           g1(x, a7,c7,s7) + g1(x, a8,c8,s8)

def g9(x, a1,c1,s1, a2,c2,s2, a3,c3,s3, a4,c4,s4, a5,c5,s5,
       a6,c6,s6, a7,c7,s7, a8,c8,s8, a9,c9,s9):
    return g1(x, a1,c1,s1) + g1(x, a2,c2,s2) + g1(x, a3,c3,s3) + \
           g1(x, a4,c4,s4) + g1(x, a5,c5,s5) + g1(x, a6,c6,s6) + \
           g1(x, a7,c7,s7) + g1(x, a8,c8,s8) + g1(x, a9,c9,s9)

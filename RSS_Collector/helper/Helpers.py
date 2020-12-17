# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 16:14:06 2020

@author: Faroud
"""
import hashlib
   
def build_id_from_str(chain):
    """Buil a hashed object of type SHA-256

    Parameters
    ----------
    chain : str
        chain used to build the hash.

    Returns
    -------
    str
        the utf-8 encoded chain of the built hash.

    """
    return hashlib.sha256(chain.encode('utf-8')).hexdigest()#.encode('utf-8')
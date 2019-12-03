#!/usr/bin/env python3
# coding: utf-8
"""
title: crypt_helpers.py
date: 2019-12-01
author: jskrable
description: cipher classes for RSA and El Gamal
"""

import math
import crypt_helpers as cp

class RSA:

    def __init__(self):
        # make these strong primes???
        self.__p = cp.prime_search(3)
        self.__q = cp.prime_search(3)
        self.n = self.__p * self.__q
        self.__phi = (self.__p - 1) * (self.__q - 1)
        self.e = cp.blum_blum_shub(20) % self.__phi


    def encrypt(self, message):
        """
        function to encrypt a message, given a public key made up of
        a modulus and an exponent. raises the message to the exponent
        in modular group and returns the encrypted message.
        """
        return cp.fast_exp(message, self.e, self.n)


    def decrypt(self, message):
        """
        function to decrypt a message encrypted using RSA, given a public
        key made up of a modulus and an exponent. calculates the decryption
        exponent using the extended euclidean algorithm and exponentiates 
        to solve the decryption.
        """
        # d = cp.phi(self.mod) + cp.ext_gcd(cp.phi(self.mod), self.e)[-1]
        d = self.__phi + cp.ext_gcd(self.__phi, self.e)[-1]
        return cp.fast_exp(message, d, self.n)


    def crack(self, message):
        """
        function to crack RSA encryption using pollard's rho??
        get p and 1 by factoring n, calculate phi using that, get 
        d using that.
        """
        return -1


class ElGamal:

    def __init__(self, mod):
        if not cp.miller_rabin(mod, 30):
            raise Exception('Modulus is not prime. Cannot safely encrypt. Please provide a prime modulus at class initialization.')
            return -1
        self.mod = mod
        self.base = cp.primitive_root_search(self.mod)
        self.__key_A = cp.blum_blum_shub(20) % self.mod
        self.key_pub = cp.fast_exp(self.base, self.__key_A, self.mod)


    def encrypt(self, message):
        """
        function to encrypt a message, given 

        """
        if message > self.mod:
            raise Exception('Message larger than modular group. Cannot safely encrypt. Please provide larger modulus at class initialization.')
            return -1, -1
        key_B = cp.blum_blum_shub(20) % self.mod
        c1 = cp.fast_exp(self.base, key_B, self.mod)
        c2 = (cp.fast_exp(self.key_pub, key_B, self.mod) * message) % self.mod
        return c1, c2


    def decrypt(self, key, message):
        """
        function to decrypt a message encrypted using el gamal, given the
        publically transmitted key from Bob, the encrypted message from Bob,
        and the previously known key_A that Alice chose during initialization.

        """
        s = cp.fast_exp(key, self.__key_A, self.mod)
        decrypted = (cp.fast_exp(s, self.mod-2, self.mod) * message) % self.mod
        return decrypted


    def crack(self, c1, c2):
        """
        function to crack el gamal encryption using baby step giant step. takes in
        the following publically transmitted information:
        c1: the base taken to key_B power
        c2: the encrypted message
        key_pub: transmitted by Alice to begin the protocol
        base: transmitted by Alice to begin the protocol
        mod: the mutually agreed upon modular group, public knowledge

        uses baby step giant step to solve for Alice and Bob's keys, then decrypts
        the message using the same method as Alice.

        note key_A is derived here by solving a discrete log, not using the class's 
        private key_A attribute Alice saved earlier.
        """

        def baby_step_giant_step(a, b, mod):
            """
            solves discrete log problem given an answer a, log base b, and
            modular group mod.
            """
            n = cp.phi(mod)
            m = math.ceil((n**0.5) % mod)
            # more efficient to store in dict
            # j = [(j, (b**j) % mod) for j in range(0,m)]
            # this is slow, make it faster
            j = {j: cp.fast_exp(b, j, mod) for j in range(0, m)}
            # c = (b**-1)**m = b**(phi(mod)-1)**m
            c = cp.fast_exp(cp.fast_exp(b, (n - 1), mod), m, mod)
            i = {i: (a * (c ** i)) % mod for i in range(0, m)}
            shared = [(x, y) for x, vi in i.items() for y, vj in j.items() if vi == vj]
            l = [((i * m) + j) % n for i, j in shared]
            return l[0]

        key_A = baby_step_giant_step(self.key_pub, self.base, self.mod)
        # key_B = baby_step_giant_step(c1, self.base, self.mod)

        s = cp.fast_exp(c1, key_A, self.mod)
        decrypted = (cp.fast_exp(s, self.mod-2, self.mod) * c2) % self.mod

        return decrypted
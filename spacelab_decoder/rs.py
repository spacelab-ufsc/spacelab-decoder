#
# rs.py
# 
# Copyright (C) 2022, Gabriel Mariano Marcelino - PU5GMA <gabriel.mm8@gmail.com>
# 
# This file is part of PyNGHam library.
# 
# PyNGHam library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyNGHam library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with PyNGHam library. If not, see <http://www.gnu.org/licenses/>.
# 
#


import math

class RS:
    """
    Reed-Solomon class.
    """

    def __init__(self, symsize, gfpoly, fcr, prim, nroots, pad):
        """
        Class constructor (Reed-Solomon coding configuration).

        :param symsize: Symbol size.
        :param gfpoly: Galois field polynomial.
        :param fcr: First consecutive root (index form).
        :param prim: Primitive element (index form).
        :param nroots: Number of generator roots (number of parity symbols).
        :param pad: Padding bytes in shortened block.

        :return: None.
        """
        self._mm = int()                        # Bits per symbol
        self._nn = int()                        # Symbols per block (= (1 << mm) - 1)
        self._alpha_to = [0] * (1 << symsize)   # log lookup table
        self._index_of = [0] * (1 << symsize)   # Antilog lookup table
        self._genpoly = [0] * (nroots + 1)      # Generator polynomial
        self._nroots = int()                    # Number of generator roots = number of parity symbols
        self._fcr = int()                       # First consecutive root, index form
        self._prim = int()                      # Primitive element, index form
        self._iprim = int()                     # prim-th root of 1, index form
        self._pad = int()                       # Padding bytes in shortened block

        i = int()
        j = int()
        sr = int()
        root = int()
        iprim = int()

        # Check parameter ranges
        if ((symsize < 0) or (symsize > 8)):
            return

        if ((fcr < 0) or (fcr >= (1 << symsize))):
            return

        if ((prim <= 0) or (prim >= (1 << symsize))):
            return

        if ((nroots < 0) or (nroots >= (1 << symsize))):
            return  # Can't have more roots than symbol values!

        if ((pad < 0) or (pad >= ((1 << symsize) - 1 - nroots))):
            return  # Too much padding

        self._mm = symsize
        self._nn = (1 << symsize) - 1
        self._pad = pad

        # Generate Galois field lookup tables
        self._index_of[0] = self._nn    # log(zero) = -inf
        self._alpha_to[self._nn] = 0    # alpha**-inf = 0
        sr = 1
        for i in range(self._nn):
            self._index_of[sr] = i
            self._alpha_to[i] = sr
            sr = sr << 1
            if (sr & (1 << symsize)):
                sr = sr ^ gfpoly
            sr = sr & self._nn
        if (sr != 1):
            # field generator polynomial is not primitive!
            return

        self._fcr = fcr
        self._prim = prim
        self._nroots = nroots

        # Find prim-th root of 1, used in decoding
        iprim = 1
        while(1):
            if (iprim % prim == 0):
                break
            iprim = iprim + self._nn
        self._iprim = int(iprim / prim)

        self._genpoly[0] = 1
        root = fcr * prim
        for i in range(nroots):
            self._genpoly[i + 1] = 1

            # Multiply rs->genpoly[] by  @**(root + x)
            for j in range(i, 0, -1):
                if (self._genpoly[j] != 0):
                    self._genpoly[j] = self._genpoly[j - 1] ^ self._alpha_to[self._modnn(self._index_of[self._genpoly[j]] + root)]
                else:
                    self._genpoly[j] = self._genpoly[j - 1]
            # rs->genpoly[0] can never be zero
            self._genpoly[0] = self._alpha_to[self._modnn(self._index_of[self._genpoly[0]] + root)]
            root = root + prim
        # convert rs->genpoly[] to index form for quicker encoding
        for i in range(nroots + 1):
            self._genpoly[i] = self._index_of[self._genpoly[i]]

    def __str__(self):
        """
        Represents the class as a string.

        :return: a brief description of the class.
        """
        return 'Reed-Solomon coding library'

    def _modnn(self, x):
        """
        Computes the modulo of a given number.

        :param x: is the integer to compute the modulo.

        :return: The computed modulo value of the given number.
        """
        while(x >= self._nn):
            x = x - self._nn
            x = (x >> self._mm) + (x & self._nn)

        return x;

    def encode(self, data):
        """
        Encodes a generic byte sequence.

        :param data: is the data to compute the parity sequence (list of integers).

        :return: The computed parity data.
        """
        feedback = int()

        parity = [0]*self._nroots

        for i in range(self._nn - self._nroots - self._pad):
            feedback = self._index_of[data[i] ^ parity[0]]
            if (feedback != self._nn):  # feedback term is non-zero
                for j in range(self._nroots):
	                parity[j] = parity[j] ^ self._alpha_to[self._modnn(feedback + self._genpoly[self._nroots - j])]
            # Shift
            parity.pop(0)
            if (feedback != self._nn):
                parity.append(self._alpha_to[self._modnn(feedback + self._genpoly[0])])
            else:
                parity.append(0)

        return parity

    def decode(self, data, eras_pos, no_eras):
        """
        Decode a Reed-Solomon coded byte sequence.

        :param data: is the data to decode (data + parity, list of integers).
        :param eras_pos: the error positions (list of index).
        :param no_eras: the number of errors.

        :return: The corrected data (if applicable), the number of detected errors and the error positions.
        """
        retval = -1

        deg_lambda = int()
        el = int()
        deg_omega = int()
        u = int()
        q = int()
        tmp = int()
        num1 = int()
        num2 = int()
        den = int()
        discr_r = int()
        _lambda = [0] * (self._nroots + 1)    # Err+Eras Locator poly and syndrome poly
        s = [0] * self._nroots
        b = [0] * (self._nroots + 1)
        t = [0] * (self._nroots + 1)
        omega = [0] * (self._nroots + 1)
        root = [0] * self._nroots
        reg = [0] * (self._nroots + 1)
        loc = [0] * self._nroots
        syn_error = int()
        count = int()

        # form the syndromes; i.e., evaluate data(x) at roots of g(x)
        for i in range(self._nroots):
            s[i] = data[0]

        for j in range(1, self._nn - self._pad):
            for i in range(self._nroots):
                if (s[i] == 0):
                    s[i] = data[j]
                else:
                    s[i] = data[j] ^ self._alpha_to[self._modnn(self._index_of[s[i]] + (self._fcr + i) * self._prim)]

        # Convert syndromes to index form, checking for nonzero condition
        syn_error = 0
        for i in range(self._nroots):
            syn_error = syn_error | s[i]
            s[i] = self._index_of[s[i]]

        if (not syn_error):
            # if syndrome is zero, data[] is a codeword and there are no errors to correct. So return data[] unmodified
            count = 0;
        else:
            _lambda[0] = 1

            if (no_eras > 0):
                # Init lambda to be the erasure locator polynomial
                _lambda[1] = self._alpha_to[self._modnn(self._prim * (self._nn - 1 - eras_pos[0]))]
                for i in range(1, no_eras):
                    u = self._modnn(self._prim * (self._nn - 1 - eras_pos[i]))
                    for j in range(i + 1, 0, -1):
                        tmp = self._index_of[_lambda[j - 1]]
                        if (tmp != self._nn):
                            _lambda[j] = _lambda[j] ^ seld_.alpha_to[self._modnn(u + tmp)]
            for i in range(self._nroots + 1):
                b[i] = self._index_of[_lambda[i]]

            # Begin Berlekamp-Massey algorithm to determine error+erasure locator polynomial
            r = no_eras + 1
            el = no_eras
            while(r <= self._nroots):   # r is the step number
                # Compute discrepancy at the r-th step in poly-form
                discr_r = 0
                for i in range(r):
                    if ((_lambda[i] != 0) and (s[r - i - 1] != self._nn)):
                        discr_r = discr_r ^ self._alpha_to[self._modnn(self._index_of[_lambda[i]] + s[r - i - 1])]
                discr_r = self._index_of[discr_r]   # Index form
                if (discr_r == self._nn):
                    # 2 lines below: B(x) <-- x*B(x)
                    b.insert(0, self._nn)
                else:
                    # 7 lines below: T(x) <-- lambda(x) - discr_r*x*b(x)
                    t[0] = _lambda[0]
                    for i in range(self._nroots):
                        if (b[i] != self._nn):
                            t[i + 1] = _lambda[i + 1] ^ self._alpha_to[self._modnn(discr_r + b[i])]
                        else:
                            t[i + 1] = _lambda[i + 1]
                    if (2 * el <= r + no_eras - 1):
                        el = r + no_eras - el
                        # 2 lines below: B(x) <-- inv(discr_r) * lambda(x)
                        for i in range(self._nroots + 1):
                            if (_lambda[i] == 0):
                                b[i] = self._nn
                            else:
                                b[i] = self._modnn(self._index_of[_lambda[i]] - discr_r + self._nn)
                    else:
                        # 2 lines below: B(x) <-- x*B(x)
                        b.insert(0, self._nn)
                    _lambda = t[:self._nroots + 1]
                r = r + 1

            # Convert lambda to index form and compute deg(lambda(x))
            deg_lambda = 0
            for i in range(self._nroots + 1):
                _lambda[i] = self._index_of[_lambda[i]]
                if (_lambda[i] != self._nn):
                    deg_lambda = i
            # Find roots of the error+erasure locator polynomial by Chien search
            reg[1:] = _lambda[1:self._nroots + 1]
            count = 0   # Number of roots of _lambda(x)
            k = self._iprim - 1
            for i in range(1, self._nn + 1):
                q = 1   # lambda[0] is always 0
                for j in range(deg_lambda, 0, -1):
                    if (reg[j] != self._nn):
                        reg[j] = self._modnn(reg[j] + j)
                        q = q ^ self._alpha_to[reg[j]]
                if (q != 0):
                    k = self._modnn(k + self._iprim)
                    continue    # Not a root
                # store root (index-form) and error location number
                root[count] = i
                loc[count] = k
                # If we've already found max possible roots, abort the search to save time
                count = count + 1
                if (count == deg_lambda):
                    break
                k = self._modnn(k + self._iprim)
            if (deg_lambda != count):
                # deg(lambda) unequal to number of roots => uncorrectable error detected
                count = -1
            else:
                # Compute err+eras evaluator poly omega(x) = s(x)*lambda(x) (modulo x**rs.nroots). in index form. Also find deg(omega)
                deg_omega = deg_lambda - 1
                for i in range(deg_omega + 1):
                    tmp = 0
                    for j in range(i, -1, -1):
                        if ((s[i - j] != self._nn) and (_lambda[j] != self._nn)):
                            tmp = tmp ^ self._alpha_to[self._modnn(s[i - j] + _lambda[j])]
                    omega[i] = self._index_of[tmp]

                # Compute error values in poly-form. num1 = omega(inv(X(l))), num2 = inv(X(l))**(rs.fcr-1) and den = lambda_pr(inv(X(l))) all in poly-form
                for j in range(count - 1, -1, -1):
                    num1 = 0
                    for i in range(deg_omega, -1, -1):
                        if (omega[i] != self._nn):
                            num1 = num1 ^ self._alpha_to[self._modnn(omega[i] + i * root[j])]
                    num2 = self._alpha_to[self._modnn(root[j] * (self._fcr - 1) + self._nn)]
                    den = 0

                    # lambda[i+1] for i even is the formal derivative lambda_pr of lambda[i]
                    for i in range(min(deg_lambda, self._nroots - 1) & ~1, -1, -2):
                        if (_lambda[i + 1] != self._nn):
                            den = den ^ self._alpha_to[self._modnn(_lambda[i + 1] + i * root[j])]
                    # Apply error to data
                    if (num1 != 0 and loc[j] >= self._pad):
                        data[loc[j] - self._pad] = data[loc[j] - self._pad] ^ self._alpha_to[self._modnn(self._index_of[num1] + self._index_of[num2] + self._nn - self._index_of[den])]

        if (eras_pos != None):
            eras_pos = [0] * count
            for i in range(count):
                eras_pos[i] = loc[i]
        retval = count

        return data, retval, eras_pos

#
#  clock_recovery_mm.py
#  
#  Copyright (C) 2020, Universidade Federal de Santa Catarina
#  
#  This file is part of SpaceLab-Decoder.
#
#  SpaceLab-Decoder is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  SpaceLab-Decoder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with SpaceLab-Decoder; if not, see <http://www.gnu.org/licenses/>.
#  
#

__author__      = "Gabriel Mariano Marcelino - PU5GMA"
__copyright__   = "Copyright (C) 2020, Universidade Federal de Santa Catarina"
__credits__     = ["Gabriel Mariano Marcelino - PU5GMA"]
__license__     = "GPL3"
__version__     = "0.2.0"
__maintainer__  = "Gabriel Mariano Marcelino - PU5GMA"
__email__       = "gabriel.mm8@gmail.com"
__status__      = "Development"


from mmse_fir_interpolator_ff import mmse_fir_interpolator

import math

class ClockRecoveryMM:

    def __init__(self, omega, gain_omega, mu, gain_mu, omega_relative_limit):
        self.d_mu = mu
        self.d_gain_mu = gain_mu
        self.d_gain_omega = gain_omega
        self.d_omega_relative_limit = omega_relative_limit
        self.d_last_sample = 0
        self.d_interp = mmse_fir_interpolator()

        if omega < 1:
            raise RuntimeError("Clock rate must be > 0!")

        if gain_mu < 0 or gain_omega < 0:
            raise RuntimeError("Gains must be non-negative!")

        self.set_omega(omega)       # Also sets min and max omega
#        self._set_inverse_relative_rate(omega)

    def set_verbose(self, verbose):
        self.d_verbose = verbose

    def set_gain_mu(self, gain_mu):
        self.d_gain_mu = gain_mu

    def set_gain_omega(self, gain_omega):
        self.d_gain_omega = gain_omega

    def set_mu(self, mu):
        self.d_mu = mu

    def set_omega(self, omega):
        self.d_omega = omega
        self.d_omega_mid = omega
        self.d_omega_lim = self.d_omega_mid * self.d_omega_relative_limit

    def mu(self):
        return self.d_mu

    def omega(self):
        return self.d_omega

    def gain_mu(self):
        return self.d_gain_mu

    def gain_omega(self):
        return self.d_gain_omega

    def compute(self, inp):
        output = self.d_interp.interpolate(inp, self.d_mu)
        mm_val = self._slice(self.d_last_sample) * output - self._slice(output) * self.d_last_sample
        self.d_last_sample = output

        self.d_omega = self.d_omega + self.d_gain_omega * mm_val
        self.d_omega = self.d_omega_mid + self._branchless_clip(self.d_omega - self.d_omega_mid, self.d_omega_lim)
        self.d_mu = self.d_mu + self.d_omega + self.d_gain_mu * mm_val

        ii = ii + int(math.floor(self.d_mu))
        self.d_mu = self.d_mu - math.floor(self.d_mu)

        return output

    def _slice(self, x):
        if x < 0:
            return -1.0*x
        else:
            return 1.0*x

    def _branchless_clip(self, x, clip):
        x1 = abs(x + clip)
        x2 = abs(x - clip)
        x1 = x1 - x2

        return 0.5*x1

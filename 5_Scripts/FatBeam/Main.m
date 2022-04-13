## Copyright (C) 2021 Bruno Luna
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <https://www.gnu.org/licenses/>.

## -*- texinfo -*-
## @deftypefn {}
## Program for simplified calculation of cyclic fatigue damage on beams
## modelled by simplified approaches (Euler-Bernoulli)
##
## Use file Input.m in this same folder for entering the necessary input data.
## @end deftypefn
##
## Project: MHH Dissertation
## Author: Bruno Luna
## Created: 2021-05-23

%% Initialization
clear ; close all; clc

%% Input data
InpVec = Input;

%% Calculate moment on beam
M = SimplySupBeam(InpVec);

%% Calculate bending stress on beam
Sb = BendStr(InpVec, M);

%% Calculate damage and expected life for point with maximum bending stress
OutVec = Damage(InpVec, Sb);
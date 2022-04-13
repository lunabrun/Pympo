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
## modelled by simplified approaches (Timoshenko cantilever beam)
##
## Use file Input.m in this same folder for entering the necessary input data.
## @end deftypefn
##
## Project: MHH Dissertation
## Author: Bruno Luna
## Created: 2021-06-23
## Note: All references in source code are in the CitationKex format 
## (FirstAuthorYear, e.g. Luna2021). The title of the reference and further info
## can be find in JabRef database RefDB_BrunoLuna.bib
## 
## TO-DO (Status - 2021-08-08):
## 0 - Correct size of N for N=10e6 and N=1 in DamageJanecek2015
## 1 - Add test units (e.g., check max deformation, bending stress and damage)
## 2 - Cleanup code (info repeated in different files, e.g. plot, input etc.!)

%% Initialization
clear ; close all; clc

%% Input data
InpData = Input;

%% Calculate moment on beam
M = CantileverBeam(InpData);

%% Calculate max. bending stress on beam
Sbmax = BendStr(InpData, M);

%% Calculate max. shear stress on beam
Ssmax = ShearStr(InpData);

%% Calculate damage and expected life for point with maximum bending stress
OutData = Damage(InpData, Sbmax);


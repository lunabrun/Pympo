%% Project: MHH Dissertation
%  Title/File: BendStr.m
%  Author: Bruno Luna 
%  Date (start): 23 May 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of bending stress on beam
%
%  Main assumptions:
%  1 - Euler-Bernoulli conditions met
%  2 - Constant cross section
%  3 - Linear material (Hook law valid)
%

function Sbmax = BendStr(InpVec, M)
 
%% Setup the parameters used
I = InpVec(4);   % Second moment of area (mm^4)
c = InpVec(5);   % Distance of most outward fibers from neutral axis (mm)

%% Calculations
Sb = (M.*c)./I;      % Bending stress along beam (MPa)
Sbmax = max(abs(Sb)); % Max bending stress on beam for a given load (MPa)
endfunction
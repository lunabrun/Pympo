%% Project: MHH Dissertation
%  Title/File: Input.m
%  Author: Bruno Luna 
%  Date (start): 23 May 2021
%
%  Content
%  ------------
% 
%  This file contains the input for calculation of a beam/frame
%  representing a fixed dental prostheses in a (very) simplified
%  manner
%
%  Main assumptions:
%  1 - A ceramic fixed dental prostheses can be approximmated via a 1D beam
%      and/or 2D frame.
%  2 - See calculation *.m files for specific assumptions.
%
function InpVec = Input

%% Input values (only values to be changed manually by user!)
L = 1;   % Length of beam (mm)
P = 1;   % Value of point load (N)
E = 1;   % Young modulus (N/mm^2 [MPa])
I = 1;   % Second moment of area (mm^4)
c = 1;   % Distance of most outward fibers from neutral axis (mm)
nc = 1;  % Number of cycles for which a given load range is applied(adim)
C = 1;   % Fatigue capacity for SN curve (TO CHECK UNITS!)
m = 1;   % Exponent for SN curve (TO CHECK UNITS!)

%% Input vector for all other functions in program
InpVec = [L, P, E, I, c, nc, C, m];
endfunction
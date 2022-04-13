%% Project: MHH Dissertation
%  Title/File: Damage.m
%  Author: Bruno Luna 
%  Date (start): 23 May 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of damage on beam
%
%  Main assumptions:
%  1 - Constant cycle load (i.e., "sinus"-like load curve)
%  2 - SN curve with as a single segment (no "knee")
%  3 - All calculations valid for the input load range only
%  4 - Surely many others (model still VERY simplistic)
%

function OutVec = Damage(InpVec, Sbmax);
 
%% Setup the parameters used
nc = InpVec(6);      % Number of cycles for a load range (adim)
C = InpVec(7);       % Fatigue capacity for SN curve (TO CHECK UNITS!)
m = InpVec(8);       % Exponent for SN curve (TO CHECK UNITS!)

%% Calculations
Ni = C/(Sbmax.^m);   % Endurable number of cycles from SN curve (# of cycles)
D = nc/Ni;           % Damage by this load range and number of cycles (adim)

%% Output vector from this program
OutVec = [D, Ni];
endfunction
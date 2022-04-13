%% Project: MHH Dissertation
%  Title/File: Input.m
%  Author: Bruno Luna 
%  Date (start): 23 Jun 2021
%
%  Content
%  ------------
% 
%  This file contains the input for calculation of a beam/frame
%  representing a dental implant in a (very) simplified
%  manner
%
%  Main assumptions:
%  1 - A titanium dental implant can be approximmated via a 1D cantilever beam.
%  2 - See calculation *.m files for specific assumptions.
%  3 - Base dimensions, base loads and materials as per Kitamura2004 article (
%      see JabRef databank for thesis for more details).
%
function InpVec = Input

%% Input values (only values to be changed manually by user!)

% Cross-section of implant
dImp = 4;           % Diameter of implant (mm)
I = (pi*dImp^4)/64; % Second moment of area (mm^4)
c = dImp/2;         % Distance of most outward fibers from neutral axis (mm)
CS = [dImp, I, c];

% Length of implant
Lini = 6 + 2.8;   % Initial length of beam (mm)
LAddFac = 1.3  % Additive factor for beam in each step (mm)
LMultFac = 1.0 % Multiplicative factor for beam in each step (adim)
L = [Lini, LAddFac, LMultFac];

% Material intrinsic properties
E = 110; % Young modulus (N/mm^2 [MPa])
C = 1;   % Fatigue capacity for SN curve (TO CHECK UNITS!)
m = 1;   % Exponent for SN curve (TO CHECK UNITS!)
Mat = [E, C, m];

% Load values and corresponding cycle quantities
P = [50];  % Value of point load (N) amplitude. 
         % Buccolingually, i.e., perpendicular to beam           
nc = [1];  % Number of cycles for which a given load range is applied(adim)

%% Input vector for all other functions in program
InpVec = [CS, L, Mat, P, nc];
endfunction
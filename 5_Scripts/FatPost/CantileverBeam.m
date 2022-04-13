%% Project: MHH Dissertation
%  Title/File: CantileverBeam.m
%  Author: Bruno Luna 
%  Date (start): 02 July 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of cantilever beam
%  with concentrated load at the free extremity (end load).
%  That is, the implant is considered as a "post".
%  Timoshenko cantilever beam formulas as per Oechsner2013.
%
%  Main assumptions:
%  1 - Timoshenko ("basic" formulation) conditions met
%  2 - Constant cross section
%  3 - Linear material (Hook law valid)
%

function M = CantileverBeam(InpData)

%% Setup the parameters used
% Length of beam (mm)
L = InpData.Len.L;  % Value of lengths for each year considered (mm)
x = InpData.Len.x;  % Points to calculate beam
P = InpData.Load.P; % Value of point loads amplitude for each sub-step (N)
E = InpData.Mat.E;  % Young modulus (N/mm^2 [MPa])
G = InpData.Mat.G;  % Shear modulus (N/mm^2 [MPa])
A = InpData.CS.A;   % Area for shear stress calculation
I = InpData.CS.I;   % Second moment of area (mm^4)
Ks = InpData.CS.Ks; % Shear correction factor (e.g. 9/10 for circ. section)
np = InpData.Gen.np;% Number of points to calculate beam (adim)
Lw = InpData.Gen.Lw; % Line weight for output graphics (admin)

%% Calculations
% Function along beam (Timoshenko formulation)
d = ((P.*x.^3)/(6*E*I))-((P.*L'.*x.^2)/(2*E*I))-(P./(Ks*A*G)).*x; % Def.along beam(mm)
s = ((P.*x.^2)/(2*E*I))-(P.*L'.*x)/(E*I); % Slope along beam (rad)
M = P.*(L'-x);                            % Moment along beam (N*mm)
V = -P.*ones(length(L),length(x));        % Shear force along beam (N)

%% Plot results
figure;
for i = 1:size(d,1)
  for j = 1:size(d,3)
    subplot (2, 2, 1)
    hold on;
    plot (x(i,:), d(i,:,j), "--kd", "linewidth", Lw);
    xlabel ("x (mm)");
    ylabel ("d(x) (mm)");
    title ("Deflection");
    subplot (2, 2, 2)
    hold on;
    plot (x(i,:), s(i,:,j), "--m.", "linewidth", Lw);
    xlabel ("x (mm)");
    ylabel ("s(x) (rad)");
    title ("Slope");
    subplot (2, 2, 3)
    hold on;
    plot (x(i,:), M(i,:,j), "--r*", "linewidth", Lw);
    xlabel ("x (mm)");
    ylabel ("M(x) (N*mm)");
    title ("Moment");
    subplot (2, 2, 4)
    hold on;
    plot (x(i,:), V(i,:,j), "--bs", "linewidth", Lw);
    xlabel ("x (mm)");
    ylabel ("V(x) (N)");
    title ("Shear force");
  endfor
endfor

%% For testing/debugging only
% Max values (for debug purposes only)
R = P;                      % Reaction forces (N)
dmax = -(P.*L.^3)/(3*E*I) - (P.*L)/(Ks*A*G);  % Maximum deflection (mm)
smax = -(P.*L.^2)/(2*E*I);  % Maximum slope (rad)
Mmax = P.*L;                % Maximum moment (N*mm)
Vmax = -P;                  % Maximum shear force (N)

% Function along beam (Euler-Bernoulli for debug/comparison only)
dEuler = zeros(length(L), length(x), length(P)); % Initialize deflection vector 
dEuler = -((P.*x.^2)/(6*E*I)).*(3*L'-x); % Def. along beam(mm)
sEuler = zeros(length(L), length(x), length(P)); % Initialize slope vector 
sEuler = -((P.*x)/(2*E*I)).*(2*L'-x);    % Slope along beam (rad)
endfunction
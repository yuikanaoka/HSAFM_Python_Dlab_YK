function SimMolecule(filename,tip_radius,grid_size,phi)
%SimMolecule(filename,tip_radius,grid_size,phi)
%
% filename    ... the filename where the molecular structure (atom positions) 
%                 is defined
% tip_radius  ... the radius of the tip (paraboloid of revolution) in nanometer
% grid_size   ... the number of pixel in x-direction of the undilated molecule
% phi         ... phi = [phi_x, phi_y, phi_z]; a vector that describes the 
%                 rotation of the molecule in x, y, and z-direction, 
%                 respectively (Euler angles)
%
%
%           -------------->  x-direction
%           |
%           |
%           |
%           |
%           |
%           |
%           v
%
%      y-direction
%
  
  %start measuring the time
  tic
  
  %print out everything during program execution
  more off;
  
  %get the atom coordinates from a structure file
  coordinates = ReadCIF(filename);
  
  %rotational matrices in x, y, and z
  x_rot_m = [1,0,0;0,cos(phi(1)),-sin(phi(1));0,sin(phi(1)),cos(phi(1))];
  y_rot_m = [cos(phi(2)),0,sin(phi(2));0,1,0;-sin(phi(2)),0,cos(phi(2))];
  z_rot_m = [cos(phi(3)),-sin(phi(3)),0;sin(phi(3)),cos(phi(3)),0;0,0,1];
  
  %apply rotations to the  atom coordinates
  coordinates = coordinates*x_rot_m*y_rot_m*z_rot_m;
  
  %find the minimum values of the atom coordinates
  min_co = min(coordinates);
  
  %set the minimum values to zero (molecule is lying on the substrate)
  coordinates(:,1) -= min_co(1);
  coordinates(:,2) -= min_co(2);
  coordinates(:,3) -= min_co(3);
  
  %the structure file specifies the coordinates in Angstrom, but we want
  %them in nanometers, so divide by 10
  coordinates = coordinates/10;
  
  %get the number of the atoms
  Lc = length(coordinates(:,1));
  
  %get the maximum values of the coordinates...
  max_co = max(coordinates);
  %... and save the maximum values to new variables
  x_max = max_co(1)
  y_max = max_co(2)
  z_max = max_co(3)
  
  %set the number of pixels in x-direction according to the user input
  %the pixels in y-direction are calculated to fit the ration of x_max and y_max
  grid_size_x = grid_size;
  grid_size_y = ceil(grid_size*(y_max/x_max));
  
  %calculate how many nanometers one pixel is in x and y directions
  dx = x_max/grid_size_x
  dy = y_max/grid_size_y
  
  %determine the structure of the molecule if the tip size was only 1 px
  heightmap1px = SimMolecule1PxTip(coordinates, grid_size);
  
  %set the tip size so that the highest z-value of the molecule is equal or less
  %than the highest z-value of the tip
  i_xm = (1/dx)*sqrt(2*tip_radius*z_max);
  tip_size = 2*ceil(i_xm)+1
  
  %print the time this took so far
  toc
  
  %create a matrix so that if the tip images the molecule, the final dilated
  %image can be shown properly
  L_bx = grid_size_x + 2*tip_size;
  L_by = grid_size_y + 2*tip_size;
  heightmap_border = zeros(L_by, L_bx);
  
  %assign the 1-px-tip topography to the center of the previously created
  %heightmap (all other values are zero)
  heightmap_border(tip_size:L_by - tip_size-1,tip_size:L_bx - tip_size-1) = heightmap1px;
  
  %draw the 1-px-tip topography in such a size that the image borders are
  %identical to the borders of the dilated image, wich is caluculated
  %in the next step
  ts_half = ceil(tip_size/2);
  imshow(heightmap_border(ts_half:L_by - ts_half,ts_half:L_bx - ts_half)/max(max(heightmap_border)));
  refresh;
  
  %create a heightmap of the tip
  tip_map = MakeTip(tip_radius, tip_size, dx, dy);
  
  %cycle through all of the 1-px-tip topography map and dilate the tip with
  %the molecule
  for iy = 1:grid_size_y + tip_size
    
    for ix = 1:grid_size_x + tip_size
      
      %the tip is positioned at the surface (in direct contact) and then
      %scanned across the surface; should the tip and the molecule intersect,
      %the tip would have to move up (in z-direction) by the maximum amount
      %difference (in z) of the intersection...
      z_diff_map = heightmap_border(iy:iy+tip_size-1,ix:ix+tip_size-1) - tip_map;
      %...which is then called "displacement"
      displacement = max(max(z_diff_map));
      %the laterally resolved displacement is then identical to the dilated
      %image
      heightmap(iy,ix) = displacement;
    
    endfor
    
  endfor
  
  %print the size of the final image in pixel...
  s_hm = size(heightmap)
  %...and nanometers
  dimensions = [dx*s_hm(2), dy*s_hm(1)]
  %for reference show also the pixel that make up the 1-px-tip topography map
  grid_size_x
  grid_size_y
  
  %show the final image...
  imshow(heightmap/max(max(heightmap)));
  refresh;
  %...and save the heightmap to a text file
  save('-ascii', 'heightmap.txt', 'heightmap')
  
  %finally tell how long it took to calculate the dilated image
  toc
  
end
function XY = circle_pf(xm,ym,R,N)
  
  #x = [-R+xm:(2*R)/N:R+xm]';
  
  alpha = [0:2*pi/N:2*pi]';
  
  x = R*cos(alpha)+xm;
  y = R*sin(alpha)+ym;
  
  
  
  #(x-xm)^2 + (y-ym)^2 = R^2
  
  #y1 = sqrt(R^2 - (x-xm).^2) + ym;
  #y2 = -sqrt(R^2 - (x-xm).^2) + ym;
  
  #y = [y1;y2];
  
  #x = [x;x];
  
  XY = [x,y];
  
  #plot(x,y,'.');
  #axis([-50,50,-10,50],"equal");
  #pause
  
endfunction
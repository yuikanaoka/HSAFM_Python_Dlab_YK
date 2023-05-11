function mt2ddilation(radius,angle,tilt,dx,dy)
  
  N = 999;
  
  substrate_dim = 80;
  
  MT = make_mt(12.5,13);
  
  substrate =[(-substrate_dim:2*substrate_dim/N:substrate_dim)',zeros(N+1,1)];
  
  TIP = make_doubletip(radius,angle,tilt,50,N,dx,dy);
  
  rTIP = rasterize(substrate,TIP,1);
  rMT = rasterize(substrate,MT,0);
  
  
  PROFILE = dilation(substrate, rTIP, rMT);
  
  plot(substrate(:,1),substrate(:,2),'-k', MT(1:50:length(MT),1),MT(1:50:length(MT),2),'.k', TIP(:,1)-30,TIP(:,2),'-b', PROFILE(:,1),PROFILE(:,2),'-r')
  %plot(PROFILE(:,1),PROFILE(:,2),'-r')
  axis([-50,50,-10,40],"equal");
  
endfunction

<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.10" tiledversion="1.12.2" name="tile" tilewidth="32" tileheight="32" tilecount="200" columns="10">
 <image source="tile.png" width="320" height="640"/>
 <tile id="10">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="11">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="12">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="20">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="30">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="32">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="61">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="62">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="63">
  <properties>
   <property name="collides" type="bool" value="true"/>
  </properties>
 </tile>
 <wangsets>
  <wangset name="teste" type="corner" tile="-1">
   <wangcolor name="teste" color="#ff0000" tile="1" probability="1"/>
   <wangtile tileid="0" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="1" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="2" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="10" wangid="0,0,0,1,0,1,0,1"/>
   <wangtile tileid="11" wangid="0,0,0,1,0,1,0,0"/>
   <wangtile tileid="12" wangid="0,1,0,1,0,1,0,0"/>
   <wangtile tileid="22" wangid="0,0,0,1,0,1,0,1"/>
   <wangtile tileid="23" wangid="0,1,0,0,0,0,0,0"/>
   <wangtile tileid="24" wangid="0,0,0,1,0,0,0,0"/>
   <wangtile tileid="33" wangid="0,1,0,0,0,1,0,1"/>
   <wangtile tileid="34" wangid="0,0,0,1,0,0,0,0"/>
   <wangtile tileid="35" wangid="0,0,0,0,0,1,0,1"/>
  </wangset>
 </wangsets>
</tileset>

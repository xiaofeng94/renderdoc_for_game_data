## RenderDoc for Game data
This repo aims to acquire data from commerical games for various vision tasks whose data is difficulty to colloect. Before the start, please get familiar with the great game debugging tool [RenderDoc](https://github.com/baldurk/renderdoc).

It is still under construction and lacks of some instructions and descriptions.

## What can you get
With this codebase, you can get various intermediate outputs of the rendering pipeline of a game, including depth, meshes and textures. Below are some examples from the commercial game GTAV (Grand Theft Auto V). Note that Rockstar Games, the publisher of GTAV, allows non-commerical use of footage from the game as long as certain conditions are met. See the [policy](https://support.rockstargames.com/articles/200153756/Policy-on-posting-copyrighted-Rockstar-Games-material).

### Various info in G-Buffer
You may get the diffuse map, normal map, specular map, irradiance map and depth map as follows.


### HDR and LDR image pairs
For someone who are interested in data-driven tone mapping and reverse tone mapping, it is a good choice to get HDR and LDR image pairs from the game.


### Foggy image simulation
With images and corresponding depth, you can get clear and foggy image pairs to faciliate your defogging researches.



## Customization for Your own
To begain with, you should get to know the rendering pipeline of your target game. For GTAV, you may find useful information in this [Link](http://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study/). Then, compile the RenderDoc. Since I have just modified functions of capture and saving to save the depth maps, if you don't need those you may use the original RenderDoc. After that, capture frames you need. Finally, run the processing code in scripts/python to get what you want. I will provide concrete instructions about how to use those scripts and how to modify them. But for now, I'm just quite engaged in my personal stuffs.


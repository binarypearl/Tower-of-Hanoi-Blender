import bpy
import time
import sys

# This script moves the disks in our Tower of Hanoi animation.
# The basic setup is this:
#   There are 3 towers, with all 3 discs at rest on the left most tower.
#   After running this script:
#     The 3 discs will have moved to the middle tower per a recursive algorithm
#     Key frames will be inserted at the appropraite spots for animation.
#
# Tower of Hanoi algorithm and Stack data structure was taken from an online book:
#  Problem Soloving and Algorithms by By Brad Miller and David Ranum, Luther College
#  http://interactivepython.org/runestone/static/pythonds/index.html

# --Shaun Miller 05/16/2015

# The first thing we have here is that we define a Stack data structure.
# The reason for this is that the Tower of Hanoi towers are just that, Stacks.
# They have a First in, Last out mechanism.  

# We have a need to keep track of the discs as we take them off of a tower and place 
# them on to another one.  By pushing and popping the discs on/off of a Stack at the 
# same time that we move the discs in Blender, we are able to keep track of where they 
# are and move the dics the appropriate amount of Blender units. 

class stack_with_hole_on_right:
    def __init__(self):
        self.items = []
        
    def is_empty(self):
        return self.items == []
    
    def push(self, data_to_push):
        self.items.append(data_to_push)
        
    def pop(self):
        return self.items.pop()
    
    def peek(self):
        return self.items[len(self.items)-1]
    
    def size(self):
        return len(self.items)
    
    def print_all(self):
        print (self.items)

# This is the main class that does just about everything that we need to do.
# This is invoked at the very bottom of the script something like this:

# hanoi_object = hanoi()
# hanoi_object.move_tower (3, "tower_a", "tower_b", "tower_c")

# Where 3 is the height, and then we pass a unique name for each tower.
# The algorithm itself can handle more discs by simply chaning the number and
# adding additional disc names, but I don't have all of the mechanisms 
# in place to just increase this here from a Blender perspective.

class hanoi:
    # This is our constructor (Well apparently it's not really a consturctor because Python has already
    # created the class), but __init__(self) has same functionality of a constructor in other 
    # Object Oriented languages in that it's called as soon as you create the object. 
     
    def __init__(self):
        # Create 3 stacks to keep track of which disks are on which towers.
        self.tower_a_stack = stack_with_hole_on_right()
        self.tower_b_stack = stack_with_hole_on_right()
        self.tower_c_stack = stack_with_hole_on_right()
    
        # Pushing our 3 rings onto the first (left-most) Stack. 
        # The smallest ring is "ring_size_1" and the largest ring is "ring_size_3".
        # So we push the larger ring first "ring_size_3", as it goes on to the bottom.    
        self.tower_a_stack.push("ring_size_3")
        self.tower_a_stack.push("ring_size_2")
        self.tower_a_stack.push("ring_size_1")
   
        # Lets define a frame rate.  That way we can increase frames by this amount, and if we decide 
        # to change the frame rate later, we only have to change it in this code in one spot.
        self.frame_rate = 24
        
        # This will hold what frame that we are currently on.  Basically each time we have a movement,
        # we will run the code:  self.frame_count += frame_rate
        self.frame_count = 0      

        # Set initial keyframes:
        
        # The nice thing about this is that we are inserting keyframes on a specific object.
        # Other examples I have seen use bpy.context.object.keyframe_insert(args),
        # which is confusing to me as I don't know which object I was setting the keyframes on.
        # By using bpy.data.objects["name"].keyframe_insert(args). I know that the keyframes that I want to insert
        # are getting inserted on the specifc objects that I intended.
        bpy.data.objects["ring_size_3"].keyframe_insert(data_path='location', frame=self.frame_count)
        bpy.data.objects["ring_size_2"].keyframe_insert(data_path='location', frame=self.frame_count)
        bpy.data.objects["ring_size_1"].keyframe_insert(data_path='location', frame=self.frame_count)
        
        # The debugging here is a litte over complicated, mainly because I wasn't sure what
        # was happening originally, and I also intended to show explanations during the animation
        # (but I didn't get that far).
        #
        # So what we do is to append the text that we want to see into a class variable called self.debug_buffer.
        # At the end, we will take the entire buffer and display the entire text as one text object.
        bpy.ops.object.text_add(location=(10,0,10), rotation=(90,0,0))
        
        self.ob = bpy.context.object
        self.ob.name = 'text_object_debug'
        self.tcu = self.ob.data
        self.tcu.name = 'text_tcu_debug'
        self.tcu.body = ""
        
        self.debug_buffer = ""
        
        # The self.iter_count was used to stop the animation at certain points for debugging.
        # Beyond that it's not used anywhere else.  I already commented it out, but I had a 
        # little if statement in the move_tower() routine below that would stop the 
        # routine early if it hit a certain number.
        self.iter_count = 0

    # This is the actual recursive Tower of Hanoi algorithm.  
    # See here for explanation:  http://interactivepython.org/runestone/static/pythonds/Recursion/TowerofHanoi.html
    def move_tower(self, height, from_pole, to_pole, with_pole):
        if height >= 1:
            self.iter_count += 1   
            
            self.move_tower(height-1, from_pole, with_pole, to_pole)
            self.move_disk(from_pole, to_pole)
            self.move_tower(height-1, with_pole, to_pole, from_pole)
            
    # The tricky thing about keyframes is that you have consider all of your objects that have motion
    # at all points in time.  So it's not just moving 1 disc in this case. 
    # Even though only 1 disc moves at a time, we have to consider the other discs that are just sitting there,
    # otherwise they will start moving prematurely.       
    
    # So basically what we do is once we move a disc, we pass that name into this function.
    # Then it looks at the other 2 discs and inserts a keyframe for them as well at the passed in frame.
    # That way the other 2 discs will stay put while another disc is being moved.   
    def keep_other_discs_at_rest(self, disc_to_not_keep_at_rest, frame_to_insert_keyframe):
         if disc_to_not_keep_at_rest == "ring_size_1":
             bpy.data.objects["ring_size_2"].keyframe_insert(data_path='location', frame=frame_to_insert_keyframe)
             bpy.data.objects["ring_size_3"].keyframe_insert(data_path='location', frame=frame_to_insert_keyframe)
             
         elif disc_to_not_keep_at_rest == "ring_size_2":
             bpy.data.objects["ring_size_1"].keyframe_insert(data_path='location', frame=frame_to_insert_keyframe)
             bpy.data.objects["ring_size_3"].keyframe_insert(data_path='location', frame=frame_to_insert_keyframe)
             
         elif disc_to_not_keep_at_rest == "ring_size_3":
             bpy.data.objects["ring_size_1"].keyframe_insert(data_path='location', frame=frame_to_insert_keyframe)
             bpy.data.objects["ring_size_2"].keyframe_insert(data_path='location', frame=frame_to_insert_keyframe)        
    
    
    # The move_disk() function is over complicated and could be simplified, but I didn't get that far.
    # But it still worked as is.
    
    # Basically there are 3 if/elif conditions, one if our source tower is "tower_a", "tower_b" and "tower_c".
    # I'm only going to describe one block, as they essentially all have the same logic, it's just a matter of 
    # what our source tower is and what our destination tower is.
    
    # How the movement is scaled:
    # Moving a disk is a 3 step process:
    #  1.  Move the disk up the z axis
    #  2.  Move the disk left or right on x axis
    #  3.  Move the disk down the z axis
    
    # My goal was to use integer blender units, but due to the complexity of this,
    # I didn't quite fully get it scaled that way.  
    # So for z axis movement, I got it down to 0.5 increments, which is still easy enough to work with.
    # For x axis, I did get it down to just integers.
    
    # So for the z axis movements, we will move up or down by either 6, 6.5, or 7 Blender units.
    # Basically the discs will move up to the same height.  So it the disc is on the bottom,
    # it will move up 7 units.  If there are 2 discs, it will move up 6.5, and if there are 3 discs,
    # the disc being moved will move up 6 units.
    
    # For the x axis movements, we will either move 5 Blender units to the left or right to move 
    # one tower over, or 10 Blender units if moving two towers over.
    
    # The rest of the comments for this block are written above each apprioate line.
    # I only did this for one of the blocks as the same logic applies to the other 
    # 2 code blocks as well. 
    
################################################################################            
    def move_disk(self, from_pole, to_pole):

        # So we see which tower is our source tower and which tower is our destination.
        self.debug_buffer = "\n\nFrom pole: " + from_pole + "\n" + "To pole:     " + to_pole + "\n"   

        if from_pole == "tower_a":
            length_of_tower_a_stack = self.tower_a_stack.size()  # Getting the length of the stack to determine how many
                                                                 # Blender units to move up/down.
            top_disc_on_tower_a = self.tower_a_stack.peek()  # Peeks looks at the top entry but doesn't remove it.
            
            self.debug_buffer += "The length of tower_a_stack is: " + str(length_of_tower_a_stack) + "\n"
            self.debug_buffer += "Peeking top disc on tower a is: " + top_disc_on_tower_a + "\n"
            
            # Key frames are tricky.  Here is the process:
            # Assume you already have previous keyframes set (which we did in hanoi.__init__(self):
            #   1.  Change the frame count to the new frame.  In this case we are always bumping up by 24 frames 
            #       (aka self.frame_rate).
            #   2.  Move our object.  In this case, the length that we move up the z axis is determined by the
            #       spot that the disc in question is on.
            #   3.  Set our new key frames.  This involes:
            #       1.  Setting our keyframe on the object in question.
            #       2.  Calling self.keep_other_discs_at_rest() for the other discs.
            
           
            # BEGIN: This block is for moving the disc up the z axis:
            
            self.frame_count += self.frame_rate            
            if length_of_tower_a_stack == 3:  
                bpy.data.objects[top_disc_on_tower_a].location.z += 6
                self.debug_buffer += "I see 3 discs on source tower a so I move up z axis by 6.\n"
                    
            elif length_of_tower_a_stack == 2:
                bpy.data.objects[top_disc_on_tower_a].location.z += 6.5
                self.debug_buffer += "I see 2 discs on source tower a so I move up z axis by 6.5.\n"    
                    
            elif length_of_tower_a_stack == 1:
                bpy.data.objects[top_disc_on_tower_a].location.z += 7
                self.debug_buffer += "I see 1 discs on source tower a so I move up z axis by 7.\n"
    
            bpy.data.objects[top_disc_on_tower_a].keyframe_insert(data_path='location', frame=self.frame_count)
            self.keep_other_discs_at_rest(top_disc_on_tower_a, self.frame_count - self.frame_rate)
            
            
            self.debug_buffer += "KFD: I inserted a key frame on: " + top_disc_on_tower_a + " at frame: " + str(self.frame_count) + "\n"
            self.debug_buffer += "KFD: I inserted a key frame on the other 2 discs at frame: " + str(self.frame_count - self.frame_rate) + "\n"
    
            # END: This block is for moving the disc up the z axis:
    
            # BEGIN: This block is for moving the disc across the x axis:
            if to_pole == "tower_b":
                length_of_tower_b_stack = self.tower_b_stack.size()
                self.debug_buffer += "The length of tower_b_stack is: " + str(length_of_tower_b_stack) + "\n"
                
                self.frame_count += self.frame_rate  
                bpy.data.objects[top_disc_on_tower_a].location.x += 5
                bpy.data.objects[top_disc_on_tower_a].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(top_disc_on_tower_a, self.frame_count - self.frame_rate) 
                
                self.debug_buffer += "KFD: I inserted a key frame on: " + top_disc_on_tower_a + " at frame: " + str(self.frame_count) + "\n"
                self.debug_buffer += "KFD: I inserted a key frame on the other 2 discs at frame: " + str(self.frame_count - self.frame_rate) + "\n"                              
                
                # Now that we have actually removed the disc from the tower, let's pop it off the stack,
                # and save it temporarily in the "poppsed_disc" variable, as we will need to push it back
                # on to a new stack soon.
                popped_disc = self.tower_a_stack.pop()

                self.debug_buffer += "I am moving: " + top_disc_on_tower_a + " to the right on the x axis by 5.\n"
                
                # END: This block is for moving the disc across the x axis:
                
                # BEGIN: This block is for moving the disc down the z axis:
                self.frame_count += self.frame_rate 
                
                if length_of_tower_b_stack == 0:
                    bpy.data.objects[popped_disc].location.z -= 7
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 7 on the z axis.\n"
                    
                elif length_of_tower_b_stack == 1:
                    bpy.data.objects[popped_disc].location.z -= 6.5
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6.5 on the z axis.\n"
                    
                elif length_of_tower_b_stack == 2:
                    bpy.data.objects[popped_disc].location.z -= 6                
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6 on the z axis.\n"
                  
                # One thing to note here, I have to called self.keep_other_discs_at_rest() twice here,
                # once for the normal run, and another time one second beforehand.  Otherwise
                # certain keyframes were getting missed and then discs were moving prematurely.  
                bpy.data.objects[popped_disc].keyframe_insert(data_path='location', frame=self.frame_count) 
                self.keep_other_discs_at_rest(popped_disc, self.frame_count - self.frame_rate)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count)
                
                
                self.debug_buffer += "KFD: I inserted a key frame on: " + popped_disc + " at frame: " + str(self.frame_count) + "\n"
                self.debug_buffer += "KFD: I inserted a key frame on the other 2 discs at position: " + str(self.frame_count - self.frame_rate) + "\n"                
                    
                # Now we push our previously popped off disc and push it on to the new destination stack.     
                self.tower_b_stack.push(popped_disc)    

            elif to_pole == "tower_c":                    
                length_of_tower_c_stack = self.tower_c_stack.size()
                self.debug_buffer += "The length of tower_c_stack is: " + str(length_of_tower_c_stack) + "\n"

                self.frame_count += self.frame_rate  
                bpy.data.objects[top_disc_on_tower_a].location.x += 10
                bpy.data.objects[top_disc_on_tower_a].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(top_disc_on_tower_a, self.frame_count - self.frame_rate) 
                
                self.debug_buffer += "KFD: I inserted a key frame on: " + top_disc_on_tower_a + " at frame: " + str(self.frame_count) + "\n"
                self.debug_buffer += "KFD: I inserted a key frame on the other 2 discs at position: " + str(self.frame_count - self.frame_rate) + "\n"                
                                
                popped_disc = self.tower_a_stack.pop() 
                
                self.debug_buffer += "I am moving: " + top_disc_on_tower_a + " to the right on the x axis by 10.\n"   

                self.frame_count += self.frame_rate

                if length_of_tower_c_stack == 0:
                    bpy.data.objects[popped_disc].location.z -= 7
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 7 on the z axis.\n"
                    
                elif length_of_tower_c_stack == 1:
                    bpy.data.objects[popped_disc].location.z -= 6.5
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6.5 on the z axis.\n"
                    
                elif length_of_tower_c_stack == 2:
                    bpy.data.objects[popped_disc].location.z -= 6
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6 on the z axis.\n"
                
                bpy.data.objects[popped_disc].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count - self.frame_rate)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count)

                self.debug_buffer += "KFD: I inserted a key frame on: " + popped_disc + " at frame: " + str(self.frame_count) + "\n"
                self.debug_buffer += "KFD: I inserted a key frame on the other 2 discs at frame: " + str(self.frame_count - self.frame_rate) + "\n"
                    
                self.tower_c_stack.push(popped_disc) 
                  

################################################################################
            
################################################################################                        
        elif from_pole == "tower_b":
            length_of_tower_b_stack = self.tower_b_stack.size()
            top_disc_on_tower_b = self.tower_b_stack.peek()
            
            self.debug_buffer += "The length of tower_b_stack is: " + str(length_of_tower_b_stack) + "\n"
            self.debug_buffer += "Peeking top disc on tower b is: " + top_disc_on_tower_b + "\n"
            
            self.frame_count += self.frame_rate
            
            if length_of_tower_b_stack == 3:     
                bpy.data.objects[top_disc_on_tower_b].location.z += 6
                self.debug_buffer += "I see 3 discs on source tower b so I move up z axis by 6.\n"
                    
            elif length_of_tower_b_stack == 2:
                bpy.data.objects[top_disc_on_tower_b].location.z += 6.5
                self.debug_buffer += "I see 2 discs on source tower b so I move up z axis by 6.5.\n"
                    
            elif length_of_tower_b_stack == 1:
                bpy.data.objects[top_disc_on_tower_b].location.z += 7
                self.debug_buffer += "I see 1 discs on source tower b so I move up z axis by 7.\n"             
            
            bpy.data.objects[top_disc_on_tower_b].keyframe_insert(data_path='location', frame=self.frame_count)
            self.keep_other_discs_at_rest(top_disc_on_tower_b, self.frame_count - self.frame_rate)
            
            
          
            if to_pole == "tower_a":
                length_of_tower_a_stack = self.tower_a_stack.size()
                self.debug_buffer += "The length of tower_a_stack is: " + str(length_of_tower_a_stack) + "\n"
                
                self.frame_count += self.frame_rate
                bpy.data.objects[top_disc_on_tower_b].location.x -= 5
                bpy.data.objects[top_disc_on_tower_b].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(top_disc_on_tower_b, self.frame_count - self.frame_rate)

                popped_disc = self.tower_b_stack.pop()                 
                
                self.debug_buffer += "I am moving: " + top_disc_on_towerb + " to the left on the x axis by 5.\n"
                
                self.frame_count += self.frame_rate
                if length_of_tower_a_stack == 0:
                    bpy.data.objects[popped_disc].location.z -= 7
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 7 on the z axis.\n"
                    
                elif length_of_tower_a_stack == 1:
                    bpy.data.objects[popped_disc].location.z -= 6.5
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6.5 on the z axis.\n"
                    
                elif length_of_tower_a_stack == 2:
                    bpy.data.objects[popped_disc].location.z -= 6
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6 on the z axis.\n"
                
                bpy.data.objects[popped_disc].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count - self.frame_rate)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count)
                    
                self.tower_a_stack.push(popped_disc)                                      

            elif to_pole == "tower_c":                    
                length_of_tower_c_stack = self.tower_c_stack.size()
                self.debug_buffer += "The length of tower_c_stack is: " + str(length_of_tower_c_stack) + "\n"

                self.frame_count += self.frame_rate
                bpy.data.objects[top_disc_on_tower_b].location.x += 5
                bpy.data.objects[top_disc_on_tower_b].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(top_disc_on_tower_b, self.frame_count - self.frame_rate)
                
                popped_disc = self.tower_b_stack.pop()                     
                
                self.debug_buffer += "I am moving: " + top_disc_on_tower_b + " to the right on the x axis by 5.\n" 

                self.frame_count += self.frame_rate
                if length_of_tower_c_stack == 0:
                    bpy.data.objects[popped_disc].location.z -= 7
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 7 on the z axis.\n"
                    
                elif length_of_tower_c_stack == 1:
                    bpy.data.objects[popped_disc].location.z -= 6.5        
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6.5 on the z axis.\n"
                    
                elif length_of_tower_c_stack == 2:
                    bpy.data.objects[popped_disc].location.z -= 6     
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6 on the z axis.\n" 
                 
                bpy.data.objects[popped_disc].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count - self.frame_rate)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count)
                                    
                self.tower_c_stack.push(popped_disc)    

################################################################################  

################################################################################ 
        elif from_pole == "tower_c":
            length_of_tower_c_stack = self.tower_c_stack.size()
            top_disc_on_tower_c = self.tower_c_stack.peek()

            self.debug_buffer += "The length of tower_c_stack is: " + str(length_of_tower_c_stack) + "\n"
            self.debug_buffer += "Peeking top disc on tower c is: " + top_disc_on_tower_c + "\n"
            
            self.frame_count += self.frame_rate
            if length_of_tower_c_stack == 3:     
                bpy.data.objects[top_disc_on_tower_c].location.z += 6
                self.debug_buffer += "I see 3 discs on source tower c so I move up z axis by 6.\n"
                    
            elif length_of_tower_c_stack == 2:
                bpy.data.objects[top_disc_on_tower_c].location.z += 6.5
                self.debug_buffer += "I see 2 discs on source tower c so I move up z axis by 6.5.\n"
                    
            elif length_of_tower_c_stack == 1:
                bpy.data.objects[top_disc_on_tower_c].location.z += 7
                self.debug_buffer += "I see 1 discs on source tower c so I move up z axis by 7.\n"
            
            bpy.data.objects[top_disc_on_tower_c].keyframe_insert(data_path='location', frame=self.frame_count)
            
            if to_pole == "tower_a":
                length_of_tower_a_stack = self.tower_a_stack.size()
                self.debug_buffer += "The length of tower_a_stack is: " + str(length_of_tower_a_stack) + "\n"
                
                self.frame_count += self.frame_rate
                bpy.data.objects[top_disc_on_tower_c].location.x -= 10
                bpy.data.objects[top_disc_on_tower_c].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(top_disc_on_tower_c, self.frame_count - self.frame_rate)  

                popped_disc = self.tower_c_stack.pop()                 
                
                self.frame_count += self.frame_rate
                if length_of_tower_a_stack == 0:
                    bpy.data.objects[popped_disc].location.z -= 7
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 7 on the z axis.\n"
                    
                elif length_of_tower_a_stack == 1:
                    bpy.data.objects[popped_disc].location.z -= 6.5
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6.5 on the z axis.\n"
                    
                elif length_of_tower_a_stack == 2:
                    bpy.data.objects[popped_disc].location.z -= 6
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6 on the z axis.\n"
                
                bpy.data.objects[popped_disc].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count - self.frame_rate)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count)
                    
                self.tower_a_stack.push(popped_disc) 

            elif to_pole == "tower_b":                    
                length_of_tower_b_stack = self.tower_b_stack.size()
                self.debug_buffer += "The length of tower_b_stack is: " + str(length_of_tower_b_stack) + "\n"

                self.frame_count += self.frame_rate
                bpy.data.objects[top_disc_on_tower_c].location.x -= 5
                bpy.data.objects[top_disc_on_tower_c].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(top_disc_on_tower_c, self.frame_count - self.frame_rate)                 
                
                popped_disc = self.tower_c_stack.pop()               

                self.frame_count += self.frame_rate
                if length_of_tower_b_stack == 0:
                    bpy.data.objects[popped_disc].location.z -= 7
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 7 on the z axis.\n"
                    
                elif length_of_tower_b_stack == 1:
                    bpy.data.objects[popped_disc].location.z -= 6.5
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6.5 on the z axis.\n"
                    
                elif length_of_tower_b_stack == 2:
                    bpy.data.objects[popped_disc].location.z -= 6
                    self.debug_buffer += "I am moving: " + popped_disc + " down by 6 on the z axis.\n"
               
                bpy.data.objects[popped_disc].keyframe_insert(data_path='location', frame=self.frame_count)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count - self.frame_rate)
                self.keep_other_discs_at_rest(popped_disc, self.frame_count)
                    
                self.tower_b_stack.push(popped_disc)    
                                
                   
################################################################################ 

# And now we create our hanoi object, and then call move_tower() with a height of 3
# and the names of the towers (any name will work as long as they are unique).
hanoi_object = hanoi()
hanoi_object.move_tower (3, "tower_a", "tower_b", "tower_c")

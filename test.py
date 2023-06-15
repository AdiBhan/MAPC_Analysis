def shift(s, shifts):
    s = list(s)
    
    for i in range(len(s)):
        # sum up all shifts from i to the end of the list
        total_shift = sum(shifts[i:])
        print(ord(s[i]), i , " " , str((ord(s[i]) - ord('a') + total_shift) % 26))
        print(chr(17))
        
        numerical_difference_btwn_char_and_original = ord(s[i]) - ord('a') # with this we can get the original char
        
        new_char = numerical_difference_btwn_char_and_original + total_shift # with this we can get the new char
        
        new_char = new_char % 26 # with this we can get the new char in the range of 0-25
        
        new_char = new_char + ord('a') # with this we can get the new char in the range of a-z (97-122)
        
        new_char = chr(new_char) # with this we can get the new char in the range of a-z (97-122)
        
        s[i] = new_char # we update the char
        
    return "".join(s)
        
        
        
        
        
        # calculate new ASCII value and ensure it falls within the range of lowercase letters
        new_ascii_val = ord('a') + (ord(s[i]) - ord('a') + total_shift) % 26
        # update character
        s[i] = chr(new_ascii_val)
    return "".join(s)

print(shift("abc", [3,5,9]))
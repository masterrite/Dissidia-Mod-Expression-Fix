# Dissidia-Mod-Expression-Fix

A simple python script that fixes unmapped expressions in some mods made with Dissidia Modding Suite (don't remember if it's 0.1.0 or 0.66BETA). Script written by Claude. Readme by me.

The script fixes the names of expression targets that don't point at the model's own face texture, and rebuilds the expression sheets (_01a, _11a) in the face texture's palette. The fix will match the colors of the eyes and mouth to that of the face to avoid seams. Should work with most mods that use the same face texture and expression sheet layouts as the game files.

# Usage

Download fix_expr.py from the files, drag and drop to anywhere, and open a powershell in its location (in the shift + right click menu). Then:

```
python fix_expr.py input_edat output_edat")
```
Input edat should be the largest edat file in the mod folder, which contains the GMO. Drag the edat file into powershell. Output edat will be the fixed file. Name this yourself, or just drag the input file there again and add "_fixed" to the file name.

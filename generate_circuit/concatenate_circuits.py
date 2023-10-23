import re
import sys
import os
import threading

# circuit with sdc : c17, c1355, ac97_ctrl, aes_core, c17_slack, c1908, c2670, c3540, c3_slack, c432, c499, c5315, c6288, c7552
#                    c7552_slack, c880, des_perf, s1196, s1494, s27, s27_spef, s344, s349, s386, s400, s510, s526, vga_lcd, 

file1_set = set()
file2_set = set()


def read_two_files(file1, file2):

  with open(file1, "r") as f1, open(file2, "r") as f2:
    file1_lines = f1.readlines()
    file2_lines = f2.readlines()

  return [file1_lines,file2_lines]

def process_file_v(file1, file2, file1_lines, file2_lines, output_file_path):
  global file1_set
  global file2_set

  with open(output_file_path, "a") as f:
    for line1 in file1_lines:
      if "input" in line1:
        strings = line1.split();
        file1_set.add(strings[1][:-1]);
        #print("input " + strings[1][:-1])
        line1 = re.sub(r"^input\s+(\w+)", r"input A_\1", line1)
      elif "output" in line1:
        strings = line1.split();
        file1_set.add(strings[1][:-1]);
        #print("output " + strings[1][:-1])
        line1 = re.sub(r"^output\s+(\w+)", r"output A_\1", line1)
      elif "wire" in line1:
        if ";" in line1:
          strings = line1.split();
          file1_set.add(strings[1][:-1]);
          #print("wire " + strings[1][:-1])
        line1 = re.sub(r"^wire\s+(\w+)", r"wire A_\1", line1)
      elif "inst" in line1:
        strings = line1.split();
        file1_set.add(strings[1])
        line1 = re.sub(r"inst(\w+)", r"A_inst\1", line1)
        line1 = re.sub(r'\.([^(]*)\(([^)]*)\)', r'.\1(A_\2)', line1)
      elif "module" in line1 and "end" not in line1:
        line1 = "module " + file1 + '_' + file2 + ' (\n' 
        #line1 = re.sub(r"^module\s+(\w+)", r"module file2_\1", line1)
      elif "end" in line1:
        continue
      elif "//" in line1:
        pass 
      else:
        # the last line of module from first file
        if ");" in line1:
          line1 = re.sub(r"(\w+)", r"A_\1", line1)
          line1 = line1[:-3] + ',\n'
          f.write(line1)
          for line2 in file2_lines:
            if ("module" not in line2) and \
               ("//" not in line2)     and \
               ("input" not in line2)  and \
               ("output" not in line2) and \
               ("wire" not in line2)   and \
               ("inst" not in line2):
              line2 = re.sub(r"(\w+)", r"B_\1", line2)
              f.write(line2)
          continue
        else:
          line1 = re.sub(r"(\w+)", r"A_\1", line1)

      f.write(line1)

    for line2 in file2_lines:
      if "Start" in line2:
        f.write('\n')
      elif "input" in line2:
        strings = line2.split();
        file2_set.add(strings[1][:-1]);
        #print("input " + strings[1][:-1])
        line2 = re.sub(r"^input\s+(\w+)", r"input B_\1", line2)
      elif "output" in line2:
        strings = line2.split();
        file2_set.add(strings[1][:-1]);
        #print("input " + strings[1][:-1])
        line2 = re.sub(r"^output\s+(\w+)", r"output B_\1", line2)
      elif "wire" in line2:
        if ";" in line2:
          strings = line2.split();
          file2_set.add(strings[1][:-1]);
          #print("input " + strings[1][:-1])
        line2 = re.sub(r"^wire\s+(\w+)", r"wire B_\1", line2)
      elif "inst" in line2:
        strings = line2.split()
        file2_set.add(strings[1])
        line2 = re.sub(r"inst(\w+)", r"B_inst\1", line2)
        line2 = re.sub(r'\.([^(]*)\(([^)]*)\)', r'.\1(B_\2)', line2)
      elif "endmodule" in line2:
        pass
      else:
        continue
      f.write(line2)

def process_file_spef(file1_path, file2_path, output_file_path):
  with open(file1_path, "r") as f:
    with open(output_file_path, "a") as fout:
      lines = f.readlines()
      pattern = r'\b(' + '|'.join(file1_set) + r')\b'
      for line in lines:
        line = re.subn(pattern, r'A_\1', line)
        fout.write(line[0])

  first_new_line = True
  with open(file2_path, "r") as f:
    with open(output_file_path, "a") as fout:
      lines = f.readlines()
      pattern = r'\b(' + '|'.join(file2_set) + r')\b'
      if first_new_line == True:
        if line == '\n':
          first_new_line = False
      else:
        for line in lines:
          line = re.subn(pattern, r'B_\1', line)
          fout.write(line[0])

def process_file_sdc(file1_path, file2_path, output_file_path):
  with open(file1_path, "r") as f:
    with open(output_file_path, "a") as fout:
      lines = f.readlines()
      for line in lines:
        line = re.subn(r'\b(' + '|'.join(file1_set) + r')\b', r'A_\1', line)
        fout.write(line[0])

  with open(file2_path, "r") as f:
    with open(output_file_path, "a") as fout:
      lines = f.readlines()
      for line in lines:
        line = re.subn(r'\b(' + '|'.join(file2_set) + r')\b', r'B_\1', line)
        fout.write(line[0])

if __name__ == "__main__":

  file1_v_path = sys.argv[1] + '.v'
  file2_v_path = sys.argv[2] + '.v'
  output_v_path    = sys.argv[1] + "_" + sys.argv[2] + ".v"
  output_spef_path = sys.argv[1] + "_" + sys.argv[2] + ".spef"
  output_sdc_path  = sys.argv[1] + "_" + sys.argv[2] + ".sdc"

  if os.path.exists(output_v_path):
    os.remove(output_v_path)
  
  if os.path.exists(output_spef_path):
    os.remove(output_spef_path)
  
  if os.path.exists(output_sdc_path):
    os.remove(output_sdc_path)

  file1_lines, file2_lines = read_two_files(file1_v_path, file2_v_path)

  process_file_v(sys.argv[1], sys.argv[2], file1_lines, file2_lines, output_v_path)

  t1 = threading.Thread(target=process_file_spef, args=(sys.argv[1]+'.spef', sys.argv[2]+'.spef', output_spef_path))
  t2 = threading.Thread(target=process_file_sdc, args=(sys.argv[1]+'.sdc', sys.argv[2]+'.sdc', output_sdc_path))
 
  # starting thread 1
  t1.start()
  # starting thread 2
  t2.start()
 
  # wait until thread 1 is completely executed
  t1.join()
  # wait until thread 2 is completely executed
  t2.join()


  #process_file_spef(sys.argv[1]+'.spef', sys.argv[2]+'.spef', output_spef_path)
  
  #process_file_sdc(sys.argv[1]+'.sdc', sys.argv[2]+'.sdc', output_sdc_path)



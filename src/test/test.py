import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from limnogropher import limnograph


#im = limnograph("./src/test/input_samples/del.jpg", output_path="./src/test/output_samples/output.png")
#im = limnograph("./src/test/input_samples/polarity.png", output_path="./src/test/output_samples/output.png")
#im = limnograph("./src/test/input_samples/heightmap1.png", output_path="./src/test/output_samples/output.png")
im = limnograph("./src/test/input_samples/england.jpg", output_path="./src/test/output_samples/output.png")
im.process_images()
im.generate_sources(400, 1.4)
im.generate_rivers(10)
im.printarray()
im.render()
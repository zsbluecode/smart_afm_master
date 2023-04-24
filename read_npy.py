import numpy as np
input_data = np.load("my_array_2023-03-30_16-03-32.npy")
print(input_data.shape)
data = input_data.reshape(1,-1)
print(data.shape)
print(data)
np.savetxt("my_array_2023-03-30_16-03-32.txt",data,delimiter=',')
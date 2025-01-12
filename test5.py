import math

#loss = [0.2805, 0.1206, 0.3255, 0.3510, 0.1326]
#accuracy = [0.9182, 0.9364, 0.9091, 0.9273, 0.9455]

loss = [0.0026, 0.0134, 0.0748, 0.0015, 0.0013]
accuracy = [0.9851, 0.9851, 0.9701, 1, 1]

print(f"Best validation loss:{sum(loss)/5:.4f}")
print(f"Test accuracy:{sum(accuracy)/5:.4f}")
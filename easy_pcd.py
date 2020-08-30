import numpy as np

class PcdHeader(object):
    def __init__(self):
        self.comment = "# .PCD v.7 - Point Cloud Data file format"
        self.version = ".7"
        self.fields = "x y z"
        self.size = "4 4 4"
        self.type = "F F F"
        self.count = "1 1 1"
        self.width = 0
        self.height = 1
        self.view_point = "0 0 0 1 0 0 0"
        self.points = 0
        self.data = "ascii"

    def __repr__(self):
        header = ""
        header += "{}\n".format(self.comment)
        header += "VERSION {}\n".format(self.version)
        header += "FIELDS {}\n".format(self.fields)
        header += "SIZE {}\n".format(self.size)
        header += "TYPE {}\n".format(self.type)
        header += "COUNT {}\n".format(self.count)
        header += "WIDTH {}\n".format(self.width)
        header += "HEIGHT {}\n".format(self.height)
        header += "VIEWPOINT {}\n".format(self.view_point)
        header += "POINTS {}\n".format(self.points)
        header += "DATA {}\n".format(self.data)
        return header

    def __str__(self):
        return self.__repr__()


class EasyPcd(object):
    def __init__(self):
        self.header = PcdHeader()
        self.data = None
    
    @staticmethod
    def from_numpy(numpy_array):
        shape = numpy_array.shape
        rows = shape[0]
        pcd = EasyPcd()
        pcd.header.width = rows
        pcd.header.points = rows
        pcd.data = numpy_array
        return pcd

    def save_to_disk(self, path):
        if self.data is None:
            raise Exception("Empty Data")
        with open(path, "w") as f:
            f.write("{}".format(self.header))
            for row in self.data:
                x = row[0]
                y = row[1]
                z = row[2]
                f.write("{} {} {}\n".format(x, y, z))


if __name__ == "__main__":
    num = 5000
    points = []
    for i in range(num):
        x = np.sqrt(i * 0.25)
        y = 1000.0 * np.sin(x)
        z = 500.0 * np.cos(x)
        points.append(x)
        points.append(y)
        points.append(z)
    data = np.array(points)
    data = data.reshape((num, 3))

    pcd = EasyPcd.from_numpy(data)
    pcd.save_to_disk("a.pcd")
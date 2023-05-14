### Object Identity in the State class
Objects in the world can just be Python objects, although there are many other ways to represent them (the [predication contract](devhowtoPredicationContract) doesn't care). 

Because we will be copying the `State` object when changes are made, we will need some way to identify that, for example, the `foo` folder in one `State` object is the same `foo` folder in another `State` object. To do this, we'll give each object a unique ID by creating a base class called `UniqueObject`. It will create a member variable called `unique_id` with a UUID (a globally unique number) in it. Then, we'll derive all the objects in the system from it. That way, objects will always have a unique ID that follows them even if they are copied. 

Here's how we'll create classes for each "type of thing" in our file system world:
~~~
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(UniqueObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        

class File(UniqueObject):
    def __init__(self, name, size=None):
        super().__init__()
        self.name = name
        self.size = size
~~~

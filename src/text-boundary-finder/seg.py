class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class Seg:
    total_count = 0
    match_count = 0
    def __init__(self):
        self.head = None
        self.first_node = None
        self.last_node = None
        self.matches = []
        self.real_match = None

    def push(self, data):
        new_node = Node(data)
        if self.head is not None:
            new_node.prev = self.head
            self.head.next = new_node 
        else:
            self.first_node = new_node
        self.head = new_node
        self.last_node = new_node

    def getLen(self, head,end_node):
        temp = head
        len = 0
        while (temp != end_node):
            len += 1
            temp = temp.next
        return len

    def getMiddle(self,start_node,end_node):
        head = start_node
        if head != None:
            len = self.getLen(head,end_node)
            temp = head
            midIdx = len // 2
            while midIdx != 0:
                temp = temp.next
                midIdx -= 1
            return temp


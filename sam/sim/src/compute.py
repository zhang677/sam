from .base import *


class Compute2(Primitive, ABC):
    def __init__(self, depth=1, **kwargs):
        super().__init__(**kwargs)

        self.in1 = []
        self.in2 = []

        if self.get_stats:
            self.in1_size = 0
            self.in2_size = 0
            self.cycles_operated = 0
        self.curr_out = None

        self.backpressure = []
        self.data_ready = True
        self.branches = []
        self.depth = depth

    def check_backpressure(self):
        j =0
        for i in self.backpressure:
            if not i.fifo_available(self.branches[j]):
                return False
            j += 1
        return True

    def fifo_available(self, br = ""):
        if br == "in1" and len(self.in1) > self.depth:
            return False
        if br == "in2" and len(self.in2) > self.depth:
            return False
        #if len(self.in1) > 1 or len(self.in2) > 1:
        #    return False
        return True

    def add_child(self, child= None, branch = ""):
        self.backpressure.append(child)
        self.branches.append(branch)

    def set_in1(self, in1):
        if in1 != '' and in1 is not None:
            self.in1.append(in1)

    def set_in2(self, in2):
        if in2 != '' and in2 is not None:
            self.in2.append(in2)

    def out_val(self):
        return self.curr_out

    def compute_fifos(self):
        if self.get_stats:
            self.in1_size = max(self.in1_size, len(self.in1))
            self.in2_size = max(self.in2_size, len(self.in2))

    def print_fifos(self):
        print("Compute block in 1: ", self.in1_size)
        print("Compute block in 2: ", self.in2_size)

    def return_statistics(self):
        if self.get_stats:
            dic = {"cycle_operation": self.cycles_operated}
            dic.update(super().return_statistics())
        else:
            dic = {}
        return dic


class Add2(Compute2):
    def __init__(self, neg1=False, neg2=False, **kwargs):
        super().__init__(**kwargs)
        self.fill_value = 0
        self.neg1 = neg1
        self.neg2 = neg2

        self.get1 = True
        self.get2 = True

        self.curr_in1 = ''
        self.curr_in2 = ''

    def update(self):
        self.update_done()
        if len(self.in1) > 0 or len(self.in2) > 0:
            self.block_start = False

        if len(self.in1) > 0 and len(self.in2) > 0:
            if self.get1:
                self.curr_in1 = self.in1.pop(0)
            if self.get2:
                self.curr_in2 = self.in2.pop(0)

            if self.curr_in1 == 'D' or self.curr_in2 == 'D':
                # Inputs are both the same and done tokens
                assert (self.curr_in1 == self.curr_in2)
                self.curr_out = self.curr_in1
                self.get1 = True
                self.get2 = True
                self.done = True
            elif is_stkn(self.curr_in1) and isinstance(self.curr_in2, int):
                # FIXME: Patch for union for b(i)+C(i,j)*d(j)
                self.curr_out = self.curr_in2 + self.fill_value
                self.get1 = False
                self.get2 = True
            elif is_stkn(self.curr_in2) and isinstance(self.curr_in1, int):
                # FIXME: Patch for union for b(i)+C(i,j)*d(j)
                self.curr_out = self.curr_in1 + self.fill_value
                self.get1 = True
                self.get2 = False
            elif is_stkn(self.curr_in1) and is_stkn(self.curr_in2):
                # Inputs are both the same and stop tokens
                assert self.curr_in1 == self.curr_in2, "Both must be the same stop token: " + str(self.curr_in1) + \
                                                       " != " + str(self.curr_in2)
                self.curr_out = self.curr_in1
                self.get1 = True
                self.get2 = True
            else:
                # Both inputs are values
                self.curr_out = (-1) ** self.neg1 * self.curr_in1 + (-1) ** self.neg2 * self.curr_in2
                if self.get_stats:
                    self.cycles_operated += 1
                self.get1 = True
                self.get2 = True
            self.compute_fifos()
            if self.debug:
                print("DEBUG: Curr Out:", self.curr_out, "\t Curr In1:", self.curr_in1, "\t Curr In2:", self.curr_in2)
        else:
            self.curr_out = ''


class Multiply2(Compute2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fill_value = 0

        self.get1 = True
        self.get2 = True

        self.curr_in1 = ''
        self.curr_in2 = ''

    def update(self):
        self.update_done()
        if (len(self.in1) > 0 or len(self.in2) > 0):
            self.block_start = False

        if len(self.in1) > 0 and len(self.in2) > 0:
            #print("tokens : ", self.curr_in1, self.curr_in2, " ", self.in1, " ", self.in2)
            if self.get1:
                self.curr_in1 = self.in1.pop(0)
            if self.get2:
                self.curr_in2 = self.in2.pop(0)
            if self.curr_in1 == 'D' or self.curr_in2 == 'D':
                # Inputs are both the same and done tokens
                assert self.curr_in1 == self.curr_in2, "Both must be done tokens: " + str(self.curr_in1) + " != " + \
                                                       str(self.curr_in2)
                self.curr_out = self.curr_in1
                self.get1 = True
                self.get2 = True
                self.done = True
            elif is_stkn(self.curr_in1) and isinstance(self.curr_in2, int):
                # FIXME: Patch for union for b(i)+C(i,j)*d(j)
                self.curr_out = self.fill_value
                self.get1 = False
                self.get2 = True
            elif is_stkn(self.curr_in2) and isinstance(self.curr_in1, int):
                # FIXME: Patch for union for b(i)+C(i,j)*d(j)
                self.curr_out = self.fill_value
                self.get1 = True
                self.get2 = False
            elif is_stkn(self.curr_in1) and is_stkn(self.curr_in2):
                # Inputs are both the same and stop tokens
                #print("Check : ", self.curr_in1, " ", self.curr_in2)
                assert self.curr_in1 == self.curr_in2, "Both must be the same stop token: " + str(self.curr_in1) + \
                                                       " != " + str(self.curr_in2)
                self.curr_out = self.curr_in1
                self.get1 = True
                self.get2 = True
            else:
                # Both inputs are values
                self.curr_out = self.curr_in1 * self.curr_in2
                if self.get_stats:
                    self.cycles_operated += 1
                self.get1 = True
                self.get2 = True
            self.compute_fifos()
            if self.debug:
                print("DEBUG: MULT: \t "
                      "Curr Out:", self.curr_out, "\t Curr In1:", self.curr_in1, "\t Curr In2:", self.curr_in2)
        else:
            self.curr_out = ''


class Multiply2_back(Compute2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fill_value = 0

        self.get1 = True
        self.get2 = True

        self.curr_in1 = ''
        self.curr_in2 = ''

    def update(self):
        self.update_done()
        self.data_ready = False
        if self.check_backpressure():
            self.data_ready = True
            if (len(self.in1) > 0 or len(self.in2) > 0):
                self.block_start = False

            if len(self.in1) > 0 and len(self.in2) > 0:
                if self.get1:
                    self.curr_in1 = self.in1.pop(0)
                if self.get2:
                    self.curr_in2 = self.in2.pop(0)
                if self.curr_in1 == 'D' or self.curr_in2 == 'D':
                    # Inputs are both the same and done tokens
                    assert self.curr_in1 == self.curr_in2, "Both must be done tokens: " + str(self.curr_in1) + " != " + \
                                                           str(self.curr_in2)
                    self.curr_out = self.curr_in1
                    self.get1 = True
                    self.get2 = True
                    self.done = True
                elif is_stkn(self.curr_in1) and isinstance(self.curr_in2, int):
                    # FIXME: Patch for union for b(i)+C(i,j)*d(j)
                    self.curr_out = self.fill_value
                    self.get1 = False
                    self.get2 = True
                elif is_stkn(self.curr_in2) and isinstance(self.curr_in1, int):
                    # FIXME: Patch for union for b(i)+C(i,j)*d(j)
                    self.curr_out = self.fill_value
                    self.get1 = True
                    self.get2 = False
                elif is_stkn(self.curr_in1) and is_stkn(self.curr_in2):
                    # Inputs are both the same and stop tokens
                    assert self.curr_in1 == self.curr_in2, "Both must be the same stop token: " + str(self.curr_in1) + \
                                                           " != " + str(self.curr_in2)
                    self.curr_out = self.curr_in1
                    self.get1 = True
                    self.get2 = True
                else:
                    # Both inputs are values
                    self.curr_out = self.curr_in1 * self.curr_in2
                    if self.get_stats:
                        self.cycles_operated += 1
                    self.get1 = True
                    self.get2 = True
                self.compute_fifos()
                if self.debug:
                    print("DEBUG: MULT: \t "
                          "Curr Out:", self.curr_out, "\t Curr In1:", self.curr_in1, "\t Curr In2:", self.curr_in2)
            else:
                self.curr_out = ''
        else:
            if self.debug:
                print("DEBUG: MULT: \t "
                      "Curr Out:", self.curr_out, "\t Curr In1:", self.curr_in1, "\t Curr In2:", self.curr_in2)

class Employee:

    #class variables-shared by all instances
    num_of_employee = 0
    raise_amount = 1.04
    
    #init method acts as a contructor in python 
    def __init__(self,first,last,pay):
        self.first = first
        self.last = last
        self.pay = pay
        Employee.num_of_employee += 1

    @property
    def fullname(self):
        return '{} {}'.format(self.first,self.last)
    #setter method 
    @fullname.setter
    def fullname(self,name):
        first,last = name.split(' ')
        self.first = first
        self.last = last

    @property
    def email(self):
        return '{}.{}@gmail.com'.format(self.first,self.last)
    @email.setter
    def email(self,email):
        first,last = email.split('@')[0].split('.')
        self.first = first
        self.last = last
    
    def annual_bonus(self):
        self.pay = int(self.pay * self.raise_amount) 

    
       
#intance creation        
emp_1 = Employee('Fatima','Azfar',30000)
emp_2 = Employee('Faiqa','Azfar',40000)

#tested working of property decorator and need for a setter method
print(emp_1.email)
emp_1.email = 'adan.zia@gmail.com'
print(emp_1.email)

print(emp_1.fullname)
emp_1.fullname = 'uswah nadir'
print(emp_1.fullname)


#you can access the class variable from both the class and the instance
print(Employee.num_of_employee)

emp_1.raise_amount = 2.00
print(emp_1.__dict__)

print(Employee.raise_amount)
print(emp_2.raise_amount)
print(emp_1.raise_amount)

    
    

    
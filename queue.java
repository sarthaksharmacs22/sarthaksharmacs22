import java.util.Scanner;

import stack1.node;

class queue1 {
    static class node {
        int data;
        node next;

        node(int data){
            this.data;
            this.next;
        }

        node f = null;
        node r = null;
    }

    public void enqueue(Scanner sc) {
        System.out.println("enter data");
        int data = sc.nextInt();
        node new_node = new node(data);
        if (f == null) {
            f = new_node;
            r = new_node;
        } else {
            r.next = new_node;
            r = new_node;
        }
    }

    public void dequeue() {
        if (f == null) {
            System.out.println("underflow");
        } else {
            f = f.next;
        }
    }

    public void display() {
        node temp = f;
        while (temp != null) {
            System.out.println(temp.data);
            temp = temp.next;
        }
    }
}

public class queue {
    public static void main(String[] args) {
        int d;
        Scanner sc= new Scanner(System.in);
        queue1 s= new queue1();
        int l;
do{
    System.out.println("enter 1 to enqueue");
    System.out.println("enter 2 to dequeue");
    System.out.println("3 to display");
    d=sc.nextInt();
    switch (d) {
        case 1:
        {
            s.enqueue(sc);
            break;
        }
        case 2:
        {
            s.dequeue();
            break;
        }    
        case 3:
        {
            s.display();
            break;
        }   System.out.println("enter 0 to go back");
    }System.out.println("enter any key to exit");
    l=sc.nextInt()
    }   while(l==0)
        System.out.println("exited succesfully");
    }
}

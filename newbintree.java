
import java.util.Scanner;

public class newbintree {
    public newbintree() {

    }

    private static class node {
        int value;
        node left;
        node right;

        public node(int value) {
            this.value = value;
        }
    }

    private node root;

    public void populate(Scanner sc) {
        System.out.println("enter the root node");
        int value = sc.nextInt();
        root = new node(value);
        populate(sc, root);
    }

    private void populate(Scanner sc, node node) {
        System.out.println("Do you want to add the value to the left of" + " " + node.value);
        boolean left = sc.nextBoolean();
        if (left) {
            System.out.println("enter the value of node on the left of " + " " + node.value);
            int value = sc.nextInt();
            node.left = new node(value);
            populate(sc, node.left);
        }
        System.out.println("Do you want to add the value to the right of" + " " + node.value);
        boolean right = sc.nextBoolean();
        if (right) {
            System.out.println("enter the value of node on the right of " + " " + node.value);
            int value = sc.nextInt();
            node.right = new node(value);
            populate(sc, node.right);
        }
    }

    public void display() {
        display(root, "");
    }

    private void display(node node, String indent) {
        if (node == null) {
            return;
        }
        System.out.println(indent + node.value);
        display(node.left, indent + "\t");
        display(node.right, indent + "\t");
    }

    public void prettydisplay() {
        prettydisplay(root, 0);
    }

    private void prettydisplay(node node, int level) {
        if (node == null) {
            return;
        }
        prettydisplay(node.right, level + 1);
        if (level != 0) {
            for (int i = 0; i < level - 1; i++) {
                System.out.println("|\t\t");
            }
            System.out.println("|--------->" + node.value);
        } else {
            System.out.println(node.value);
        }
        prettydisplay(node.left, level + 1);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        newbintree tree = new newbintree();
        tree.populate(sc);
        tree.prettydisplay();
    }
}

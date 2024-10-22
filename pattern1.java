public class pattern1 {
    public static void main(String[] args) {
        pattern2(4);
    }

    static void pattern2(int n) {
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++)
                System.out.print("*");
        }
        System.out.println();
    }
}

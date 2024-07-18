#include <stdio.h>
#include <string.h>

// 无效函数
int sum(int x, int y){
	return x+y;
}

// 自定义函数1: 打印字符串长度
void printStringLength(char *str) {
    int length = strlen(str);
    printf("The length of the string is: %d\n", length);
}

// 自定义函数2: 复制并反转字符串
void reverseAndCopy(char *dest, char *src) {
    int len = strlen(src);
    memcpy(dest, src, len + 1); // 包括空字符
    int i;
    for(i=0; i < len / 2; i++) {
        char temp = dest[i];
        dest[i] = dest[len - i - 1];
        dest[len - i - 1] = temp;
    }
}

int main() {
    char input[100];
    char reversed[100];
    int *array[100] = {0};
    int x = 0;
    int *ptr;
    //*ptr = 10;
    int array_int[10];
    array_int[8] = 0;

    // 使用 gets 输入字符串，注意：gets 在 C99 中已废弃，这里仅用于示例
    printf("Enter a string: ");
    gets(input);
    gets(input);
    fgets(input, sizeof(input), stdin);

    // 调用自定义函数1打印字符串长度
    printStringLength(input);

    // 使用 scanf 和 getchar 忽略输入缓冲区中的换行符
    printf("Enter another string: ");
    getchar(); // 忽略换行符
    scanf("%99s", input);

    // 调用自定义函数2复制并反转字符串
    reverseAndCopy(reversed, input);

    // 输出反转后的字符串
    printf("Reversed string: %s\n", reversed);

    system("pause");

    return 0;
} // Make sure this closing brace is present
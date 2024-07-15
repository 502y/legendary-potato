/*
 Navicat MySQL Data Transfer

 Source Server         : 代码审计
 Source Server Type    : MySQL
 Source Server Version : 50730
 Source Host           : localhost:3306
 Source Schema         : 风险函数

 Target Server Type    : MySQL
 Target Server Version : 50730
 File Encoding         : 65001

 Date: 21/07/2022 08:09:40
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for functions
-- ----------------------------
DROP TABLE IF EXISTS `functions`;
CREATE TABLE `functions`  (
  `func_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `level` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `suggestion` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`func_name`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of functions
-- ----------------------------
INSERT INTO `functions` VALUES ('gets', '最危险', '使用更安全的fgets()函数或定义足够大的数组空间');
INSERT INTO `functions` VALUES ('strcpy', '很危险', '必须保证strDestination足够大，否则会导致溢出错误，建议改用strncpy');
INSERT INTO `functions` VALUES ('strcat', '很危险', 'dest与str所指空间不重叠，且dest要有足够空间容纳要复制的字符串，建议使用建议改用strncat');
INSERT INTO `functions` VALUES ('sprintf', '很危险', '如果str长度不够，容易造成缓冲区溢出可以用snprintf替代');
INSERT INTO `functions` VALUES ('scanf', '很危险', '输入控制符和输出参数要对应，输入之前要用printf进行输入提示，使用fgets，使用精度说明或自己解析');
INSERT INTO `functions` VALUES ('sscanf', '很危险', '在遇到非匹配项就会结束，可以使用getchar跳过字符创空格使用精度说明或自己解析，建议使用strlcpy等函数解析');
INSERT INTO `functions` VALUES ('fscanf', '很危险', '函数遇到空格和换行符时结束，使用精度说明或自己解析');
INSERT INTO `functions` VALUES ('vfscanf', '很危险', '使用精度说明符，或自己进行解析');
INSERT INTO `functions` VALUES ('vsprintf', '很危险', '建议使用使用vsnprintf');
INSERT INTO `functions` VALUES ('vscanf', '很危险', '使用精度说明符，或自己进行解析');
INSERT INTO `functions` VALUES ('vsscanf', '很危险', '使用精度说明符，或自己进行解析');
INSERT INTO `functions` VALUES ('streadd', '很危险', '确保分配的目的地参数大小是源参数大小的四倍');
INSERT INTO `functions` VALUES ('strecpy', '很危险', '确保分配的目的地参数大小是源参数大小的四倍');
INSERT INTO `functions` VALUES ('strtrns', '危险', '手工检查来查看目的地大小是否至少与源字符串相等');
INSERT INTO `functions` VALUES ('realpath', '很危险（或稍小，取决于实现）', '分配缓冲区大小为 MAXPATHLEN。同样，手工检查参数以确保输入参数不超过 MAXPATHLEN');
INSERT INTO `functions` VALUES ('syslog', '很危险（或稍小，取决于实现）', '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小');
INSERT INTO `functions` VALUES ('getopt', '很危险（或稍小，取决于实现）', '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小');
INSERT INTO `functions` VALUES ('getopt_long', '很危险（或稍小，取决于实现）', '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小');
INSERT INTO `functions` VALUES ('getpass', '很危险（或稍小，取决于实现）', '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小');
INSERT INTO `functions` VALUES ('getchar', '中等危险', '如果在循环中使用该函数，确保检查缓冲区边界');
INSERT INTO `functions` VALUES ('fgetc', '中等危险', '如果在循环中使用该函数，确保检查缓冲区边界');
INSERT INTO `functions` VALUES ('getc', '中等危险', '如果在循环中使用该函数，确保检查缓冲区边界');
INSERT INTO `functions` VALUES ('read', '中等危险', '如果在循环中使用该函数，确保检查缓冲区边界');
INSERT INTO `functions` VALUES ('bcopy', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('fgets', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('memcpy', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('snprintf', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('strccpy', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('strcadd', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('strncpy', '低危险', '确保缓冲区大小与它所说的一样大');
INSERT INTO `functions` VALUES ('vsnprintf', '低危险', '确保缓冲区大小与它所说的一样大');

SET FOREIGN_KEY_CHECKS = 1;

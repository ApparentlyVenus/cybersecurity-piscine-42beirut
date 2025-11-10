/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   source.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: odana <odana@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/07 22:19:17 by yitani            #+#    #+#             */
/*   Updated: 2025/11/10 15:14:28 by odana            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(void)
{
	char	input[24];
	char	buffer[10];

	memset(buffer, 0, 9);
	printf("Please enter key: ");
	scanf("%23s", input);
    if (input[1] != '2')
        return (printf("Nope\n"), 1);
    if (input[0] != '4')
        return (printf("Nope\n"), 1);
    int j = 0;
	for (int i = 2; i < strlen(input) && i <= 23; i +=3, j++)
	{
		char character[4] = {0};
		character[0] = input[i];
		character[1] = input[i + 1];
		character[2] = input[i + 2];

		int	ascii = atoi(character);
		buffer[j] = (char)ascii;
	}
	buffer[j] = '\0';
	if (strcmp(buffer, "*******") == 0)
		printf("Good job.\n");
	else
		return (printf("Nope.\n"), 1);
	return (0);
}

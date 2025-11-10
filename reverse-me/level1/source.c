/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   source.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: odana <odana@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/09 13:27:23 by odana             #+#    #+#             */
/*   Updated: 2025/11/09 13:32:05 by odana            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <string.h>
#include <stdio.h>

int main()
{
    char input[1024];
    printf("Please enter key: ");
    scanf("%s", input);
    if (strcmp("__stack_check", input) == 0) 
        printf("Good job.\n");
    else
        printf("Nope.\n");
    return (0);
}
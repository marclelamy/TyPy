#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_WORD_LENGTH 588721

// Structure to hold word frequency information
typedef struct {
    char word[MAX_WORD_LENGTH];
    int count;
} WordFrequency;

// Function to trim leading and trailing spaces from a string
char* trim(char* str) {
    char* end = str + strlen(str) - 1;
    while (end > str && isspace(*end))
        end--;
    *(end + 1) = '\0';

    while (*str && isspace(*str))
        str++;
    return str;
}

// Function to count the frequency of words in a given string
void countWords(const char* text, WordFrequency* wordFrequencies, int* totalWords) {
    char* word;
    char* copy = strdup(text);
    char* token = strtok(copy, " ");
    
    while (token != NULL) {
        word = trim(token);
        if (strlen(word) > 0) {
            int found = 0;
            for (int i = 0; i < *totalWords; i++) {
                if (strcmp(word, wordFrequencies[i].word) == 0) {
                    found = 1;
                    wordFrequencies[i].count++;
                    break;
                }
            }
            if (!found && *totalWords < MAX_WORD_LENGTH) {
                strcpy(wordFrequencies[*totalWords].word, word);
                wordFrequencies[*totalWords].count = 1;
                (*totalWords)++;
            }
        }
        token = strtok(NULL, " ");
    }
    
    free(copy);
}

int main() {
    // Open the file
    FILE* file = fopen("/Users/marclamy/Desktop/code/TyPy/data/text/wikipedia.txt", "r");
    if (file == NULL) {
        printf("Failed to open the file.\n");
        return 1;
    }

    // Get the file size
    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    rewind(file);

    // Allocate memory to hold the file content
    char* fileContent = (char*)malloc(fileSize + 1);
    if (fileContent == NULL) {
        printf("Failed to allocate memory for the file content.\n");
        fclose(file);
        return 1;
    }

    // Read the file content
    if (fread(fileContent, 1, fileSize, file) != fileSize) {
        printf("Failed to read the file.\n");
        free(fileContent);
        fclose(file);
        return 1;
    }
    fclose(file);

    // Initialize wordFrequencies array
    WordFrequency wordFrequencies[MAX_WORD_LENGTH];
    int totalWords = 0;
    for (int i = 0; i < MAX_WORD_LENGTH; i++) {
        wordFrequencies[i].word[0] = '\0';
        wordFrequencies[i].count = 0;
    }

    // Calculate word frequencies
    countWords(fileContent, wordFrequencies, &totalWords);

    // Output word frequencies to a CSV file
    FILE* outputFile = fopen("/Users/marclamy/Desktop/code/TyPy/data/text/word_frequencies.csv", "w");
    if (outputFile == NULL) {
        printf("Failed to open the output file.\n");
        free(fileContent);
        return 1;
    }

    fprintf(outputFile, "Word,Count\n");
    for (int i = 0; i < totalWords; i++) {
        fprintf(outputFile, "%s,%d\n", wordFrequencies[i].word, wordFrequencies[i].count);
    }

    fclose(outputFile);

    // Clean up
    free(fileContent);

    return 0;
}

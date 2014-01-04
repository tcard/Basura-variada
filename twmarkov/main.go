// This is copypasted and edited from golang.org/doc/codewalk/markov/

/*
Generating random text: a Markov chain algorithm

Based on the program presented in the "Design and Implementation" chapter
of The Practice of Programming (Kernighan and Pike, Addison-Wesley 1999).
See also Computer Recreations, Scientific American 260, 122 - 125 (1989).

A Markov chain algorithm generates text by creating a statistical model of
potential textual suffixes for a given prefix. Consider this text:

	I am not a number! I am a free man!

Our Markov chain algorithm would arrange this text into this set of prefixes
and suffixes, or "chain": (This table assumes a prefix length of two words.)

	Prefix       Suffix

	"" ""        I
	"" I         am
	I am         a
	I am         not
	a free       man!
	am a         free
	am not       a
	a number!    I
	number! I    am
	not a        number!

To generate text using this table we select an initial prefix ("I am", for
example), choose one of the suffixes associated with that prefix at random
with probability determined by the input statistics ("a"),
and then create a new prefix by removing the first word from the prefix
and appending the suffix (making the new prefix is "am a"). Repeat this process
until we can't find any suffixes for the current prefix or we exceed the word
limit. (The word limit is necessary as the chain table may contain cycles.)

Our version of this program reads text from standard input, parsing it into a
Markov chain, and writes generated text to standard output.
The prefix and output lengths can be specified using the -prefix and -words
flags on the command-line.
*/
package main

import (
	"bufio"
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

// Prefix is a Markov chain prefix of one or more words.
type Prefix []string

// String returns the Prefix as a string (for use as a map key).
func (p Prefix) String() string {
	return strings.Join(p, " ")
}

// Shift removes the first word from the Prefix and appends the given word.
func (p Prefix) Shift(word string) {
	copy(p, p[1:])
	p[len(p)-1] = word
}

// Chain contains a map ("chain") of prefixes to a list of suffixes.
// A prefix is a string of prefixLen words joined with spaces.
// A suffix is a single word. A prefix can have multiple suffixes.
type Chain struct {
	chain     map[string][]string
	prefixLen int
}

// NewChain returns a new Chain with prefixes of prefixLen words.
func NewChain(prefixLen int) *Chain {
	return &Chain{make(map[string][]string), prefixLen}
}

// Build reads text from the provided Reader and
// parses it into prefixes and suffixes that are stored in Chain.
func (c *Chain) Build(r io.Reader) {
	sc := bufio.NewScanner(r)
	for sc.Scan() {
		br := strings.NewReader(sc.Text())
		p := make(Prefix, c.prefixLen)
		for {
			var s string
			if _, err := fmt.Fscan(br, &s); err != nil {
				break
			}
			if strings.HasPrefix(s, `http`) || strings.HasPrefix(s, `@`) {
				continue
			}
			key := p.String()
			c.chain[key] = append(c.chain[key], s)
			p.Shift(s)
		}
	}
}

// Generate returns a string of at most n chars generated from Chain.
func (c *Chain) Generate(n int, nwords int) string {
	p := make(Prefix, c.prefixLen)
	var words []string
	chars := 0
	for {
		choices := c.chain[p.String()]
		if len(choices) == 0 {
			break
		}
		ri := rand.Intn(len(choices))
		next := choices[ri]
		chars += len(next) + 1
		if nwords <= 0 {
			if chars >= n {
				break
			}
		} else if len(words) == nwords {
			break
		}
		words = append(words, next)
		p.Shift(next)
	}
	// Remove words until we reach an end of sentence.
	for i := len(words) - 1; i >= 0 &&
		words[i][len(words[i])-1] != '.' &&
		words[i][len(words[i])-1] != ')' &&
		words[i][len(words[i])-1] != '?' &&
		words[i][len(words[i])-1] != '!'; i-- {
		words = words[:len(words)-1]
	}
	if len(words) == 0 {
		// Uh, try again.
		return c.Generate(n, nwords)
	}
	s := strings.Join(words, " ")

	// Let's keep punctuation balanced.
	openers := map[rune]rune{'«': '»', '(': ')', '[': ']', '¿': '?', '¡': '!'}
	closers := map[rune]rune{}
	for k, v := range openers {
		closers[v] = k
	}
	stacks := map[rune][]int{}
	for i, v := range s {
		if _, ok := openers[v]; ok {
			// Except for emoticons.
			if v == '(' && i-1 >= 0 && (s[i-1] == '=' || s[i-1] == ':') {
				continue
			}
			stacks[v] = append(stacks[v], i)
		} else if opener, ok := closers[v]; ok {
			if len(stacks[opener]) == 0 {
				// Except for emoticons.
				if v == ')' && i-1 >= 0 && (s[i-1] == '=' || s[i-1] == ':') {
					continue
				}
				stacks[v] = append(stacks[v], i)
			} else {
				stacks[opener] = stacks[opener][:len(stacks[opener])-1]
			}
		}
	}
	offset := 0
	for k, stack := range stacks {
		for _, i := range stack {
			s = s[:i-offset] + s[i-offset+len(string(k)):]
			offset += len(string(k))
		}
	}

	return s
}

func chainFromCSV(prefixLen int, f io.Reader, w io.Writer) *Chain {
	c := NewChain(prefixLen) // Initialize a new Chain.
	fcsv := csv.NewReader(f)
	tweets := ""
	i := 0
	flusher, _ := w.(http.Flusher)
	fcsv.Read()
	for row, err := fcsv.Read(); err == nil && i < 50000; row, err = fcsv.Read() {
		i += 1
		if w != nil {
			if i%100 == 0 {
				fmt.Fprintln(w, i)
				if i%1000 == 0 && flusher != nil {
					flusher.Flush()
				}
			}
		}
		tweets += row[5] + "\n"
	}
	buf := strings.NewReader(tweets)
	c.Build(buf) // Build chains from standard input.
	return c
}

func main() {
	// Register command-line flags.
	prefixLen := flag.Int("prefix", 2, "prefix length in words")
	defaultUser := flag.String("default", "tcardv", "Default user. [default].csv must be in the cwd.")

	flag.Parse()                     // Parse command-line flags.
	rand.Seed(time.Now().UnixNano()) // Seed the random number generator.

	f, _ := os.Open(*defaultUser + ".csv")
	chains := map[string]*Chain{
		*defaultUser: chainFromCSV(*prefixLen, f, os.Stdout),
	}

	http.HandleFunc("/twmarkov", func(w http.ResponseWriter, req *http.Request) {
		req.ParseForm()
		n := 140
		nwords := 0
		u := *defaultUser
		if v, ok := req.Form["n"]; ok {
			n, _ = strconv.Atoi(v[0])
		}
		if v, ok := req.Form["nwords"]; ok {
			nwords, _ = strconv.Atoi(v[0])
		}
		if v, ok := req.Form["u"]; ok {
			u = v[0]
		}

		if _, ok := chains[u]; !ok && req.Method == "POST" {
			req.ParseMultipartForm(32 << 20)
			fdata, _, err := req.FormFile("csvfile")
			if err == nil {
				chains[u] = chainFromCSV(*prefixLen, fdata, w)
				fmt.Println("ADDED", u)
			}
		}

		text := ""
		if c, ok := chains[u]; ok {
			text = c.Generate(n, nwords) // Generate text.
		} else {
			text = `<html><body>
			¡Sube!
			<form method="post" action="` + req.URL.String() + `" enctype="multipart/form-data">
			<input type="file" name="csvfile">
			<input type="submit">
			</form>
			</body></html>`
		}
		fmt.Fprintln(w, text) // Write text to standard output.
	})
	fmt.Println(http.ListenAndServe(":6060", nil))
}

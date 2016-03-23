
/* --------------------------------------------------------
 * Changeset handling
 * -------------------------------------------------------- */

/* Node class: Changeset
 *
 * Representing a diff between the last state of the graph and the current one.
 * Links to its predecessor Changeset (which is Null in case of the first
 * changeset.) 
 *
 * Adds properties:
 *  - author: string (TODO: user management, link to user)
 *  - comment: commit comment
 *  - timestamp: automatically set
 *  - changes: a list of maps, where each map represents an operation
 *      (TODO: specify precisely!)
 */
CREATE CLASS Changeset EXTENDS V
CREATE PROPERTY Changeset.author STRING
CREATE PROPERTY Changeset.comment STRING
CREATE PROPERTY Changeset.timestamp DATE
ALTER PROPERTY Changeset.timestamp default SYSDATE()
CREATE PROPERTY Changeset.changes EMBEDDEDLIST EMBEDDEDMAP

/* When adding a Changeset
cs = CREATE VERTEX Changeset SET CONTENT { ... } 
CREATE EDGE FROM cs TO (SELECT FROM Changeset WHERE in().size() = 0)
*/ 


/* --------------------------------------------------------
 * Node Classes
 * -------------------------------------------------------- */

/* Node class Node (abstract)
 *
 * Adds properties:
 *  - label: string (indexed)
 *  - last_change: a link to the last changeset modifying the node
 */
CREATE CLASS Node EXTENDS V ABSTRACT
CREATE PROPERTY Node.label STRING
CREATE INDEX Node.label NOTUNIQUE_HASH_INDEX
CREATE PROPERTY Node.last_change LINK Changeset

/* Node class: ForeignNode
 * 
 * Adds property:
 *  - language: string, iso 639-1 code
 */
CREATE CLASS ForeignNode EXTENDS Node
CREATE PROPERTY ForeignNode.language STRING


/* Node class: ArabicNode (abstract)
 *
 * The label of an ArabicNode stores one or more _fully_ vocalized arabic
 * words. Fully means that every letter has a haraka. (The UI is very likely
 * to drop sukuns and useless fathas before alifs and ta marbutas.
 *
 * TODO: Add validation regex.
 *
 * Adds property:
 *  - unvocalized_label: string (indexed)
 *    (TODO, add function generating it from label)
 */
CREATE CLASS ArabicNode EXTENDS Node ABSTRACT
CREATE PROPERTY ArabicNode.unvocalized_label STRING
CREATE INDEX ArabicNode.unvocalized_label NOTUNIQUE_HASH_INDEX


/* Node class: ArabicRoot
 *
 *  A root is not a word. Both unvocalized and vocalized label are a space
 *  separated sequence of root chars
 *
 *  Eventually add:
 *   - size (3 .. n)
 *   - foreign (yes/no)
 *
 * Allowed derivation edges:
 *  from: -
 *  to: Verb, Noun, Particle
 */
CREATE CLASS Root EXTENDS ArabicNode


/* Node class: Word (abstact)
 * Adds properties:
 *  - pattern: fully vocalized pattern 
*/
CREATE CLASS Word EXTENDS ArabicNode ABSTRACT
CREATE PROPERTY Word.pattern STRING

/* Node class: Noun
 *
 * Adds properties:
 *  - gender: one of "m", "f" and "fm" 
 *  
 * We do not add a plural property as there can be several plural forms having
 * different meanings from which different nouns can be derived. (TODO Example!)
 *
 * Allowed derivation edges:
 *  from: Root, Verb
 *  to: Noun, Collocation
 */
CREATE CLASS Noun EXTENDS Word
CREATE PROPERTY Noun.gender STRING
ALTER PROPERTY Noun.gender REGEXP "f|m|fm"


/* Node class: Verb
 *
 * Adds imperfect form - a verb having different imperfect forms is represented
 * by several nodes. This is because they might differ in meaning like مَهَرَ - يَمهَرُ 
 * as opposed to مَهَرَ - يَمهُرُ 
 *
 * Allowed derivation edges:
 *  from: Root
 *  to: Noun, Collocation
 */
CREATE CLASS Verb EXTENDS Word
CREATE PROPERTY Verb.imperfect_form STRING


/* Node class: Particle
 *
 * Allowed derivation edges:
 *  from: Root
 *  to: Noun (?), Collocation
 */
CREATE CLASS Particle EXTENDS Word


/* Node class: Collocation
 * Allowed derivation edges:
 *  from: Noun, Verb, Particle
 *  to: Noun, Collocation
 */
CREATE CLASS Collocation EXTENDS ArabicNode


/* Node class: Text
 *
 * Adds properties:
 *  - source: a string describing the origin of the text (like "Wikipedia" in the
 *            case of a Text node containing the  first sentence of a wikipedia
 *            acticle)
 *  - source_url: the url of the source (TODO add validation, see end of file) 
 *
 * Allowed derivation edges:
 *  from: *
 *  to: -
 */
CREATE CLASS Text EXTENDS ArabicNode
CREATE PROPERTY Text.source STRING
CREATE PROPERTY Text.source_url STRING


/* --------------------------------------------------------
 * Edge Classes
 * -------------------------------------------------------- */

/* Edge class: Edge
 *
 * Adds properties:
 *  - last_change: a link to the last changeset modifying the edge
 */
CREATE CLASS Edge EXTENDS E ABSTRACT
CREATE PROPERTY Edge.last_change LINK Changeset


/* Edge class: DerivationEdge
 *
 * Adds properties:
 *  - type: string, to be restricted in derived classes
 */
CREATE CLASS DerivationEdge EXTENDS Edge
CREATE PROPERTY DerivationEdge.type STRING


/* Edge class: VerbDerivationEdge
 *
 * Adds properties:
 *  - stem: str, I .. X
 */
CREATE CLASS VerbDerivationEdge EXTENDS Edge
CREATE PROPERTY DerivationEdge.stem STRING
ALTER PROPERTY DerivationEdge.stem REGEXP "I|II|III|IV|V|VI|VII|VIII|IX|X"


/* Edge class: NounDerivationEdge
 *
 * Restricts the type to be one of
 *  - ism fa'il
 *  - ism maf'ul
 *  - masdar
 *  - ism makan
 *  - ism zaman
 *  - mu'annath (so that القاهرة can connect to قاهرة)
 *  - ism dum' (so that the collocation الأمم المتحدة can connect to أمم)
 *  - naht (https://ar.wikipedia.org/wiki/لفظ_منحوت)
 *  - tarkib (?)
 *  - (TODO to be completed ...!)
 */
CREATE CLASS NounDerivationEdge EXTENDS DerivationEdge
ALTER PROPERTY NounDerivationEdge.type REGEXP "pa|pp|masdar|time|place|tool|plural|feminine"




/* Edge class: InformationEdge
 *
 * Connects ArabicNode nodes (that is roots, verbs, noun, particles and
 * collocations) to Text nodes (that is examples, definitions, explications)
 * or to ForeinNode nodes (that is translations).
 */
CREATE CLASS InformationEdge EXTENDS Edge







/*
URL validation regex:

/^[a-z](?:[-a-z0-9\+\.])*:(?:\/\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:])*@)?(?:\[(?:(?:(?:[0-9a-f]{1,4}:){6}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|::(?:[0-9a-f]{1,4}:){5}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){4}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:[0-9a-f]{1,4}:[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){3}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,2}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){2}(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,3}[0-9a-f]{1,4})?::[0-9a-f]{1,4}:(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,4}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3})|(?:(?:[0-9a-f]{1,4}:){0,5}[0-9a-f]{1,4})?::[0-9a-f]{1,4}|(?:(?:[0-9a-f]{1,4}:){0,6}[0-9a-f]{1,4})?::)|v[0-9a-f]+[-a-z0-9\._~!\$&'\(\)\*\+,;=:]+)\]|(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(?:\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}|(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=@])*)(?::[0-9]*)?(?:\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@]))*)*|\/(?:(?:(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@]))+)(?:\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@]))*)*)?|(?:(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@]))+)(?:\/(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@]))*)*|(?!(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@])))(?:\?(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@])|[\x{E000}-\x{F8FF}\x{F0000}-\x{FFFFD}\x{100000}-\x{10FFFD}\/\?])*)?(?:\#(?:(?:%[0-9a-f][0-9a-f]|[-a-z0-9\._~\x{A0}-\x{D7FF}\x{F900}-\x{FDCF}\x{FDF0}-\x{FFEF}\x{10000}-\x{1FFFD}\x{20000}-\x{2FFFD}\x{30000}-\x{3FFFD}\x{40000}-\x{4FFFD}\x{50000}-\x{5FFFD}\x{60000}-\x{6FFFD}\x{70000}-\x{7FFFD}\x{80000}-\x{8FFFD}\x{90000}-\x{9FFFD}\x{A0000}-\x{AFFFD}\x{B0000}-\x{BFFFD}\x{C0000}-\x{CFFFD}\x{D0000}-\x{DFFFD}\x{E1000}-\x{EFFFD}!\$&'\(\)\*\+,;=:@])|[\/\?])*)?$/i
*/



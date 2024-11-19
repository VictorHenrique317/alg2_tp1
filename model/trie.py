class Node:
    def __init__(self, is_end=False):
        self.children = {}
        self.labels = {}
        self.code = None
        self.is_word = is_end

class Trie:
    def __init__(self):
        self.root = Node()
        self.next_code = 256

    def insert(self, word):
      node = self.root
      index = 0

      while index < len(word) and word[index] in node.labels:
          label = node.labels[word[index]]
          i = 0

          while i < len(label) and index < len(word) and label[i] == word[index]:
              index += 1
              i += 1

          if i == len(label): 
              node = node.children[word[index - 1]]
          else:  
              self.split_node(node, word, label, i, index)
              return

      if index < len(word):
          node.labels[word[index]] = word[index:]
          node.children[word[index]] = Node(True)
          if node.children[word[index]].code is None:
              node.children[word[index]].code = self.define_code()
          elif node.children[word[index]].code != self.next_code - 1:
              pass 
      else:
          if not node.is_word: 
              node.is_word = True
          if node.code is None:
              node.code = self.define_code()


    def split_node(self, node, word, label, split_pos, word_pos):
        common_label = label[:split_pos]
        remaining_label = label[split_pos:]
        remaining_word = word[word_pos:]

        child = node.children[word[word_pos - len(common_label)]]
        new_node = Node()

        node.labels[word[word_pos - len(common_label)]] = common_label
        node.children[word[word_pos - len(common_label)]] = new_node

        new_node.labels[remaining_label[0]] = remaining_label
        new_node.children[remaining_label[0]] = child

        if remaining_word:
            new_node.labels[remaining_word[0]] = remaining_word
            new_node.children[remaining_word[0]] = Node(True)
            new_node.children[remaining_word[0]].code = self.define_code()
    
    def define_code(self):
        code = self.next_code
        self.next_code += 1
        return code
    
    def insert_list(self, words):
        for word in words:
            self.insert(word)

    def delete(self, word):
        def _delete(node, word, depth):
            if depth == len(word):  
                if not node.is_word:
                    return False  
                node.is_word = False  
                node.code = None  
                return len(node.children) == 0
    
            char = word[depth]
            if char not in node.children:
                return False  
    
            child_node = node.children[char]
            label = node.labels[char]
    
            if not word[depth:].startswith(label):
                return False 
    
            can_delete = _delete(child_node, word, depth + len(label))
    
            if can_delete:
                del node.children[char]
                del node.labels[char]
    
                return not node.is_word and len(node.children) == 0
    
            return False
    
        _delete(self.root, word, 0)

    def find_prefix(self, word):
      node = self.root
      index = 0

      while index < len(word) and word[index] in node.labels:
          label = node.labels[word[index]]
          i = 0

          while i < len(label) and index < len(word) and label[i] == word[index]:
              index += 1
              i += 1

          if i == len(label):
              node = node.children[word[index - 1]]
          else:
              return None  # Prefixo não encontrado

      if index == len(word) and node.is_word:
          return node
      return None

    def get_max_depth(self):
        return self._calculate_max_depth(self.root, 0)

    def _calculate_max_depth(self, node, depth):
        max_depth = depth
        for child in node.children.values():
            max_depth = max(max_depth, self._calculate_max_depth(child, depth + 1))
        return max_depth

    def walk_trie(self):
        return self._collect_words(self.root, "")

    def _collect_words(self, node, prefix):
        result = []
        if node.is_word:
            result.append((prefix, node.code))

        for char, label in node.labels.items():
            child = node.children[char]
            result.extend(self._collect_words(child, prefix + label))

        return result

    def find_prefix_by_code(self, target_code):
        return self._search_by_code(self.root, "", target_code)

    def _search_by_code(self, node, prefix, target_code):
        if node.is_word and node.code == target_code:
            return prefix

        for char, label in node.labels.items():
            child = node.children[char]
            result = self._search_by_code(child, prefix + label, target_code)
            if result is not None:
                return result

        return None

    def update_code(self, word, code):
      node = self.root
      for char in word:
          if char not in node.children:
              return False  # Palavra não encontrada
          node = node.children[char]
      if node.code is None:
          node.code = code
      return True

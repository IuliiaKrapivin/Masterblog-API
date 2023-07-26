from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."}
]


def invalid_post_data(data):
    """Function checks new post input"""
    if 'title' not in data:
        return "title was missed"
    elif 'content' not in data:
        return "content was missed"
    return False


def find_post_by_id(post_id):
    """Function fetches a post by its id"""
    for post in POSTS:
        if post['id'] == post_id:
            return post


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """Route returns posts data in case of GET request and saves a new post in case of POST request"""
    if request.method == 'POST':
        # Get the new post data from the client
        new_post = request.get_json()
        if invalid_post_data(new_post):
            return jsonify({"error": f"{invalid_post_data(new_post)}"}), 400

        # Generate a new ID for the post
        try:
            new_id = max(post['id'] for post in POSTS) + 1
        except ValueError:
            new_id = 1
        new_post['id'] = int(new_id)

        # Add the new post to our list
        POSTS.append(new_post)

        # Return the new post data to the client
        return jsonify(new_post), 201

    else:
        sort = request.args.get('sort')
        direction = request.args.get('direction')

        if not sort and not direction:
            # Handle simple GET request
            return jsonify(POSTS)

        # Check parameters
        if sort != 'title' and sort != 'content':
            return jsonify({"error": "sort parameter error"}), 400
        elif direction != 'asc' and direction != 'desc':
            return jsonify({"error": "direction parameter error"}), 400

        # Handle GET request with parameters
        if sort == 'title':
            filtered_titles = [val for post in POSTS for key, val in post.items() if key == 'title']
            if direction == 'asc':
                filtered_titles.sort()
                filtered_posts = [post for title in filtered_titles for post in POSTS if post['title'] == title]
            elif direction == 'desc':
                filtered_titles.sort(reverse=True)
                filtered_posts = [post for title in filtered_titles for post in POSTS if post['title'] == title]
            return jsonify(filtered_posts)
        elif sort == 'content':
            filtered_content = [val for post in POSTS for key, val in post.items() if key == 'content']
            if direction == 'asc':
                filtered_content.sort()
                filtered_posts = [post for content in filtered_content for post in POSTS if post['content'] == content]
            elif direction == 'desc':
                filtered_content.sort(reverse=True)
                filtered_posts = [post for content in filtered_content for post in POSTS if post['content'] == content]
            return jsonify(filtered_posts)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Route deletes post by its id"""
    post = find_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Not Found"}), 404
    POSTS.remove(post)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Route updates post by its id"""
    post = find_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Not Found"}), 404
    new_data = request.get_json()
    post.update(new_data)
    return jsonify(post)


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    """Route searches for a post by its title or content provided as parameters"""
    title = request.args.get('title')
    content = request.args.get('content')
    if title:
        filtered_posts = [post for post in POSTS if title.lower() in post.get('title').lower()]
        return jsonify(filtered_posts)
    elif content:
        filtered_posts = [post for post in POSTS if content.lower() in post.get('content').lower()]
        return jsonify(filtered_posts)
    else:
        return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

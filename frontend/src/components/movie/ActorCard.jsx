const ActorCard = ({ character_name, actor_name, image_url }) => {
  return (
    <div className="flex flex-col items-center w-[200px] bg-white rounded-lg shadow-md overflow-hidden">
      <div className="relative w-full h-[300px]">
        <img
          src={image_url}
          alt={actor_name}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-4 w-full">
        <h3 className="text-lg font-semibold text-gray-800 truncate">
          {actor_name}
        </h3>
        <p className="text-sm text-gray-600 truncate">{character_name}</p>
      </div>
    </div>
  );
};

export default ActorCard;
